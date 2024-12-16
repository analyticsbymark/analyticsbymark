#!/bin/sh -e
set -x

ruff check docs docs_src tests scripts --fix
ruff format docs docs_src tests scripts