#!/bin/sh -e
set -x

mypy docs_src tests
ruff check docs_src tests
ruff format docs_src tests --fix