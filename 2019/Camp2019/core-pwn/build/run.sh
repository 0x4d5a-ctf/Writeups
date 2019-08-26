#!/usr/bin/env bash
sudo docker build -t core-pwn .
sudo docker run -p 1234:1234 core-pwn
