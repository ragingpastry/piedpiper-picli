#!/bin/bash

if [[ ! $(which docker) ]]; then
  echo "Docker must be installed. Exiting"
fi

openfaas_repository="https://github.com/openfaas/faas"

function_repositories=(
  piedpiper-flake8-faas \
  piedpiper-validator-faas \
  piedpiper-cpplint-faas \
  piedpiper-pybandit-faas
)

docker swarm init
mkdir -p faas
pushd faas
git clone "${openfaas_repository}" .
./deploy_stack.sh --no-auth
curl -sL https://cli.openfaas.com | sudo sh
popd

for repository in "${function_repositories[@]}"; do
  git clone https://github.com/afcyber-dream/"${repository}"
  pushd "${repository}"
  faas build && faas deploy
  popd
done;

