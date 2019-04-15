:title: Testing

.. _testing:

Testing
=======

.. contents:: Table of Contents
    :local:

Creating a development environment
**********************************
A local development environment can be configured 
using the following Ansible collection: https://github.com/AFCYBER-DREAM/ansible-collection-pidev/

Follow these instructions to turn a new machine into a PiedPiper development environment:

.. code-block:: bash

  # the "org" variable should be the name of your Github.com organization
  org="afcyber-dream";
  
  # the "repo" variable should be the name of the repo containing your fork of afcyber-dream/ansible-collection-pidev
  repo="ansible-collection-pidev";
  
  # the "env" variable should be the nickname of the environment you wish to provision
  env="ubuntu1804/dockerswarm+openfaas"
  
  # once you have set these three variables, run this command as `root` (not a sudo user):
  bash <(curl -s https://raw.githubusercontent.com/${org}/${repo}/master/bootstrap.sh) ${org}/${repo} ${env}

After OpenFaaS has been deployed you can test functionality by using the ``faas ls`` command

Running the tests
*****************

Functional
----------
Now you can start iterating on PiCli. Basic functional tests can be found under ``tests/functional``. A script exists
at ``tests/functional/run-tests.sh`` which will run the defined functional tests. This can be used to increase
confidence that your change isn't going to break master. 

You can also run the script with tox using the ``functional`` environment

.. code-block:: bash

  tox -e functional


Lint
----
PiedPiper is linted using PEP8 and Flake8. The lint environment in tox is configured to run ``flake8`` on the picli directory.

.. code-block:: bash

  tox -e lint

