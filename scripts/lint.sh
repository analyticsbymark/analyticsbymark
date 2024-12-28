#!/bin/sh -e
set -x

mypy docs_src tests --ignore-missing-imports
ruff check docs_src tests
ruff format docs_src tests -- --fix
