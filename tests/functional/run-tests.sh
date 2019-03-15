#!/bin/sh

for project in \
    cpp_and_python_project \
    cpp_project \
    python_project; do

    echo "Running picli on project $project in $(dirname $0)/$project"
    picli --config $(dirname $0)/$project/piedpiper.d/pi_global_vars.yml lint
done