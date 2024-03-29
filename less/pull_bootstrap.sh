#!/bin/bash
# Usage: bash pull_bootstrap.sh v#.#.#

echo "$1" | grep -qP "v[0-9]+\.[0-9]+\.[0-9]+"
if [ $? -ne 0 ]; then
  echo "Not a valid Bootstrap version label: '$1'. Format: 'v#.#.#'."
  exit -1
fi

ORIGINAL_PATH=$(pwd)
ROOT=$(echo "$ORIGINAL_PATH" | grep '.*?/elf' -o -P | head -1)

cd $ROOT/less/

rm -rf ./bootstrap/
git clone git://github.com/twbs/bootstrap.git bootstrap
git add bootstrap/

cd bootstrap/
git checkout $1
nodejs /usr/bin/npm install

cd ..
ln -s bootstrap/node_modules/ node_modules

cd $ORIGINAL_PATH
