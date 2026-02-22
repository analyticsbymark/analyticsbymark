"""Shared pytest fixtures for the analyticsbymark test suite."""

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def docs_src(repo_root: Path) -> Path:
    """Return the docs_src directory for the dev site."""
    return repo_root / "projects" / "dev" / "docs_src"


@pytest.fixture
def space_dev_dir(docs_src: Path) -> Path:
    """Return the space_dev data source directory."""
    return docs_src / "space_dev"


@pytest.fixture
def spacex_dir(space_dev_dir: Path) -> Path:
    """Return the spacex dataset directory."""
    return space_dev_dir / "spacex"


@pytest.fixture
def launch_cadence_dir(spacex_dir: Path) -> Path:
    """Return the launch_cadence curiosity directory."""
    return spacex_dir / "launch_cadence"
