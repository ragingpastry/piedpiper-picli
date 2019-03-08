#!/bin/bash
pushd ../../../
python setup.py install
popd 

picli --config piedpiper.d/pi_global_vars.yml lint

