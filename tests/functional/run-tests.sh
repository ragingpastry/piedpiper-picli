#!/bin/sh

errors=0
for project in \
    cpp_and_python_project \
    cpp_project \
    python_project; do

    echo "Running picli on project $project in $(dirname $0)/$project"
    picli --config $(dirname $0)/$project/piperci.d/pi_global_vars.yml --debug validate
    if [[ $? -ne 0 ]]; then
        errors=$((errors+1))
    fi
    picli --config $(dirname $0)/$project/piperci.d/pi_global_vars.yml --debug style
    if [[ $? -ne 0 ]]; then
        errors=$((errors+1))
    fi
    picli --config $(dirname $0)/$project/piperci.d/pi_global_vars.yml --debug sast
    if [[ $? -ne 0 ]]; then
        errors=$((errors+1))
    fi
    picli --config $(dirname $0)/$project/piperci.d/pi_global_vars.yml --debug lint
    if [[ $? -ne 0 ]]; then
        errors=$((errors+1))
    fi
done

if [[ "${errors}" == 0 ]]; then
    echo "Tests ran successfully";
    exit 0;
else
    echo "Tests failed";
	exit 1;
fi
