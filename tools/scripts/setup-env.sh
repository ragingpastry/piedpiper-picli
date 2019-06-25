#!/bin/bash

if [[ ! $(which docker) ]]; then
  echo "Docker must be installed. Exiting"
fi

openfaas_repository="https://github.com/openfaas/faas"

function_repositories=(
  piperci-noop-faas
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

docker run -d -p 8089:8080 gman
docker run -d -p 9000:9000 --env MINIO_ACCESS_KEY="1EPHH13NICEJ119QPGL6" --env MINIO_SECRET_KEY="TKKUm6IAVPgAv8N++4BICQSJD5DPQqQNcuy1+k6t" -v /mnt/data:/data -v /mnt/config:/root/.minio minio/minio server /data
