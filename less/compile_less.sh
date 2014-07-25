#!/bin/bash
# Usage: bash compile_less.sh

ORIGINAL_PATH=$(pwd)
ROOT=$(echo "$ORIGINAL_PATH" | grep '.*?/elf' -o -P | head -1)

cd $ROOT/less/

nodejs /usr/bin/grunt watch

cd $ORIGINAL_PATH