#!/usr/bin/env bash

a=$(pstree -p | grep "|-server" |awk -F'[^0-9]*' '$0=$2')
sudo kill -s 9 $a
