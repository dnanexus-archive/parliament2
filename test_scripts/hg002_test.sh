#!/usr/bin/env bash

wget -q https://wiki.dnanexus.com/images/files/dx-toolkit-current-ubuntu-14.04-amd64.tar.gz
tar zxf dx-toolkit-current-ubuntu-14.04-amd64.tar.gz
source dx-toolkit/environment

mkdir -p /home/dnanexus/in
mkdir -p /home/dnanexus/out

dx login --token $DX_AUTH_TOKEN
dx select project-FQ06yF00B227FvGg5zxvk5fy

docker run dnanexus/parliament2:$TAG -h

echo "Building applet" >&1
dx build dx_app_code/parliament2 -a | jq '.id' > applet_id.txt

echo "Running applet" >&1
dx run $(cat applet_id.txt) -iiluminabam="project-FQ06yF00B227FvGg5zxvk5fy:file-Bg0b9F00pJZQV695v18Ykf7K" -iref_fasta="project-FQ06yF00B227FvGg5zxvk5fy:file-B6ZY7VG2J35Vfvpkj8y0KZ01" -iref_index="project-FQ06yF00B227FvGg5zxvk5fy:file-ByGVY4j04Y0YJ0yJpj0f8qPG" -iprefix="large_test" --yes --brief --wait --watch