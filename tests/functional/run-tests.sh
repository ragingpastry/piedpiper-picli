#!/bin/bash

errors=0
for project in \
    python_project; do

    echo "Running picli on project $project in $(dirname $0)/$project"
	pushd $(dirname $0)/$project
    picli --debug run
    if [[ $? -ne 0 ]]; then
        errors=$((errors+1))
    fi
	popd
done

if [[ "${errors}" == 0 ]]; then
    echo "Tests ran successfully";
    exit 0;
else
    echo "Tests failed";
	exit 1;
fi
