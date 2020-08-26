#!/bin/bash
PRIVATE_KEY_DIR="$HOME/.ssh"
if [ ! -e id_rsa ]
then
    cp "$PRIVATE_KEY_DIR/id_rsa" "$PWD"
fi