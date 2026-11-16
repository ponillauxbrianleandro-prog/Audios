#!/bin/bash
cd "$(dirname "$0")"; . .venv/bin/activate
for i in 1 2 3 4 5 6; do python narrar.py 2 && break; done
