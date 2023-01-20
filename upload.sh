#!/usr/bin/env bash
set -e
set -u
rsync -a $PWD/ octopi:nanoleaf-home/
