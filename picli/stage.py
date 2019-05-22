from picli.model import stage_schema
from picli import logger
from picli import util

import logging
import os
import json
from piperci.artman import artman_client
from piperci.gman import client as gman_client
from piperci.sri import generate_sri, hash_to_urlsafeb64
from piperci.gman.exceptions import TaskError
import requests
import tempfile
import zipfile

LOG = logger.get_logger(__name__)


class Stage:
    def __init__(self, stage_def, base_config):
        self.name = stage_def.get("name")
        self.stage_config = base_config
        self.dependencies = []
        self.resources = stage_def.get("resources")
        self.config = stage_def.get("config")
        self._validate(stage_def)
        if self.stage_config.debug:
            LOG.setLevel(logging.DEBUG)

    def _check_thread_status(self, thread_id=None, stage=None):
        """
        Waits for task_id to be "status". Defaults to completed
        :param thread_id: task_id string
        :param stage: The stage that the thread is tied to
        :return:
        """
        if stage is None:
            stage = self.name
        LOG.debug(f"Checking if thread_id {thread_id} has completed")
        try:
            gman_client.wait_for_thread_id_complete(
                thread_id=thread_id, gman_url=self.stage_config.gman_url, retry_max=20
            )
            self.stage_config.update_state({stage: {"state": "complete"}})
            return True
        except TimeoutError:
            message = f"Timeout detected waiting for thread_id {thread_id} to complete."
            util.sysexit_with_message(message)
        except TaskError:
            self.stage_config.update_state({self.name: {"state": "failed"}})
            event_failures = gman_client.get_thread_id_events(
                thread_id=thread_id,
                gman_url=self.stage_config.gman_url,
                query_filter=lambda x: x.get("status") == "failed",
            )
            message = (
                f"Remote job for stage {self.name} did not complete successfully."
                f"\n\n{util.safe_dump(event_failures)}"
            )
            util.sysexit_with_message(message)

    def _create_project_artifact(self):
        """
        Creates a zipfile of the project and uploads to the configured storage url
        :return: List of artifact dicts returned by util.upload_artifacts
        """
        with tempfile.TemporaryDirectory() as tempdir:
            project_artifact_file = self._zip_project(tempdir).filename
            project_artifact_name = os.path.basename(project_artifact_file)
            project_artifact_hash = generate_sri(project_artifact_file)
            sri_urlsafe = hash_to_urlsafeb64(project_artifact_hash)
            artifact_state = {self.name: {"artifacts": {project_artifact_name: {}}}}
            if artman_client.check_artifact_exists(
                artman_url=self.stage_config.gman_url, sri_urlsafe=sri_urlsafe
            ):
                LOG.debug(f"Artifact exists in ArtMan. Getting artifact data...")
                artifact = artman_client.get_artifact(
                    artman_url=self.stage_config.gman_url, sri_urlsafe=sri_urlsafe
                )
                LOG.debug(f"Artifact: {artifact}")
                artifact_state[self.name]["artifacts"][project_artifact_name] = {
                    "artifact_uri": next(art.get("uri") for art in artifact),
                    "state": "found",
                }
                self.stage_config.update_state(artifact_state)
            else:
                LOG.debug(
                    f"Artifact not found. Uploading to bucket {self.stage_config.run_id}"
                )
                self.stage_config.storage_client.upload_file(
                    self.stage_config.run_id,
                    f"artifacts/{project_artifact_name}",
                    project_artifact_file,
                )
                artifact_uri = (
                    f"minio://{self.stage_config.storage['hostname']}/"
                    f"{self.stage_config.run_id}/artifacts/"
                    f"{project_artifact_name}"
                )
                artman_client.post_artifact(
                    task_id=self.stage_config.state[self.name]["client_task_id"],
                    artman_url=self.stage_config.gman_url,
                    uri=artifact_uri,
                    caller="picli",
                    sri=str(project_artifact_hash),
                )
                artifact_state[self.name]["artifacts"][project_artifact_name] = {
                    "artifact_uri": artifact_uri,
                    "state": "uploaded",
                }
                self.stage_config.update_state(artifact_state),

    def _is_dependent_stage_state_completed(self):
        stages_not_complete = [
            stage
            for stage in self.dependencies
            if self.stage_config.state.get(stage.name)
            and self.stage_config.state.get(stage.name).get("state") != "completed"
        ]
        errors = []
        for stage in stages_not_complete:
            LOG.info(f"Checking if stage {stage.name} has completed")
            task_id_from_state = self.stage_config.state.get(stage.name).get(
                "thread_id"
            )
            if not self._check_thread_status(task_id_from_state, stage=stage.name):
                errors.append(stage.name)
        if len(errors):
            return False
        else:
            return True

    def _submit_job(self, resource_url, task_id, config=None):
        """
        Sends a PiperCI job to a remote endpoint
        :param resource_url: The URL of the endpoint
        :param task_id: task_id
        :param config: Configs to pass to the FaaS
        :return: JSON response from the endpoint
        """
        headers = {"Content-Type": "application/json"}
        task_data = {
            "run_id": self.stage_config.run_id,
            "project": self.stage_config.project_name,
            "artifacts": self.stage_config.state[self.name]["artifacts"],
            "task_id": task_id,
            "configs": config,
            "stage": self.name,
        }
        try:
            r = requests.post(resource_url, data=json.dumps(task_data), headers=headers)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            message = f"Failed to call {resource_url} gateway. \n\n{e}"
            self.stage_config.update_state({self.name: {"state": "failed"}})
            gman_client.update_task_id(
                gman_url=self.stage_config.gman_url,
                task_id=task_id,
                status="failed",
                message=f"{message}",
            )
            util.sysexit_with_message(message)
        gman_client.update_task_id(
            gman_url=self.stage_config.gman_url,
            task_id=task_id,
            status="info",
            message="Client received acceptance of job from gateway.",
        )
        self.stage_config.update_state(
            {
                self.name: {
                    "state": "running",
                    "client_task_id": task_id,
                    "thread_id": r.json().get("task").get("thread_id"),
                }
            }
        )
        return r.json()

    def _validate(self, stage_def):
        """
        Validate the loaded configuration object.
        Validations are defined in model/base_schema.py
        :return: None. Exit if errors are found.
        """
        errors = stage_schema.validate(stage_def)
        if errors:
            msg = f"Failed to validate. \n\n{errors.messages}"
            util.sysexit_with_message(msg)
        pass

    def _zip_project(self, destination):
        """
        Zips all files in the project and returns the zipfile
        object.
        :param destination: Path to create the zipfile in
        :return: ZipFile
        """
        zip_file = zipfile.ZipFile(
            f"{destination}/{self.stage_config.project_name}.zip",
            "w",
            zipfile.ZIP_DEFLATED,
        )
        for root, dirs, files in os.walk(self.stage_config.base_path):
            for file in files:

                state_path = os.path.realpath(
                    os.path.join(self.stage_config.base_path, "piperci.d/default/state")
                )
                if os.path.commonpath(
                    [os.path.abspath(state_path)]
                ) == os.path.commonpath(
                    [
                        os.path.abspath(state_path),
                        os.path.abspath(os.path.join(root, file)),
                    ]
                ):
                    continue
                else:
                    zip_file.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file), self.stage_config.base_path
                        ),
                    )

        zip_file.close()

        return zip_file

    def add_dependency(self, stage):
        """
        Add a stage object as a dependency to this stage.
        :param stage: Stage object
        :return:
        """
        self.dependencies.append(stage)

    def display(self, run_id=None):
        """
        Displays the output of the stage by downloading the log artifact into a
        temporary directory.
        :param run_id: The run_id to display
        :return: The output of the log artifact for the stage to stdout
        """
        if not run_id:
            run_id = self.stage_config.run_id
        thread_id_from_state = self.stage_config.state.get(self.name).get("thread_id")
        try:
            self._check_thread_status(thread_id=thread_id_from_state)
            LOG.debug(f"Thread has completed!")
        except TaskError:
            message = f"Waiting for job completion timed out"
            util.sysexit_with_message(message)

        LOG.info(f"Downloading log artifacts for run_id: {run_id}")
        LOG.debug(f"Checking artifacts in {run_id}/artifacts/logs/{self.name}")
        # Convert generator returned by minio to a list so we can check if
        # it's empty before iterating.
        log_artifacts = list(
            self.stage_config.storage_client.stat_file(
                run_id, f"artifacts/logs/{self.name}", recursive=True
            )
        )
        if not len(log_artifacts):
            LOG.warn(f"No log artifacts found for stage {self.name}")
        for log_artifact in log_artifacts:
            LOG.debug(f"Found log artifact {log_artifact.object_name}")
            local_path = (
                f"{self.stage_config.state_directory}/"
                f"{os.path.basename(log_artifact.object_name)}"
            )
            LOG.debug(f"Downloading log artifact {run_id}/{log_artifact.object_name}")
            self.stage_config.storage_client.storage_client.fget_object(
                run_id, log_artifact.object_name, local_path
            )
            LOG.info(f"Display artifact {log_artifact.object_name}")
            with open(local_path) as f:
                LOG.warn(f.read())

    def execute(self, wait=False):
        """
        Execute a stage.
        First we check if all of our dependent stages are complete remotely.
        Then we check if the stage we are running is already marked as complete
        in the local state file.
        Then, request a new taskID from GMan for client execution tracking.
        For every glob in the stage config we parse out which resource to invoke.
        Calls the requested resource and waits for the returned taskID to finish executing
        :param wait: Boolean. Whether to wait for results or not
        :return: None
        """
        if (
            self.stage_config.state.get(self.name)
            and self.stage_config.state.get(self.name).get("state") == "completed"
        ):
            LOG.info(
                f"Stage {self.name} marked complete in local state file. Skipping..."
            )
            return
        if not self._is_dependent_stage_state_completed():
            message = (
                f"Stage dependencies '{[dep.name for dep in self.dependencies]}' "
                f"are not complete. Check your state file"
            )
            util.sysexit_with_message(message)

        task = gman_client.request_new_task_id(
            run_id=self.stage_config.run_id,
            gman_url=self.stage_config.gman_url,
            project=self.stage_config.project_name,
            caller="picli",
            status="started",
        )
        LOG.debug(f"Received task {task} from gman")

        self.stage_config.update_state(
            {self.name: {"state": "started", "client_task_id": task["task"]["task_id"]}}
        )

        self._create_project_artifact()

        for unique_resource in {config.get("resource") for config in self.config}:
            resource_configs = [
                config
                for config in self.config
                if config.get("resource") == unique_resource
            ]
            try:
                resource_uri = next(
                    r.get("uri")
                    for r in self.resources
                    if unique_resource == r.get("name")
                )
                resource_url = self.stage_config.faas_endpoint + resource_uri
            except StopIteration:
                LOG.fatal(
                    f"Resource {unique_resource} not found in stages.yml"
                    f"for stage {self.name}.\n"
                    f"{util.safe_dump(self.resources)}"
                )
                util.sysexit_with_message("Failed")

            LOG.info(f"Sending to {resource_uri}")

            job_results = self._submit_job(
                resource_url, task.get("task").get("task_id"), config=resource_configs
            )
            LOG.debug(
                f"Job submitted for stage {self.name} to {resource_url} "
                f"with task_id {job_results.get('task').get('task_id')}"
            )

            if wait:
                self._check_thread_status(job_results.get("task").get("thread_id"))
                self.stage_config.display([self.name], self.stage_config.run_id)
