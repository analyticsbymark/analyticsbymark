"""Shared fixtures for launch_cadence tutorial tests."""

import sys
from pathlib import Path

import pytest

CURIOSITY_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CURIOSITY_DIR.parent / "data"
IMAGES_DIR = CURIOSITY_DIR / "images"

# Ensure both the curiosity folder's parent (for `from data.utils import ...`)
# and the curiosity folder itself (for direct tutorial imports) are on sys.path.
sys.path.insert(0, str(CURIOSITY_DIR.parent))
sys.path.insert(0, str(CURIOSITY_DIR))


@pytest.fixture
def curiosity_dir() -> Path:
    """Path to the launch_cadence curiosity folder."""
    return CURIOSITY_DIR


@pytest.fixture
def images_dir() -> Path:
    """Path to the images output folder."""
    return IMAGES_DIR


@pytest.fixture
def data_dir() -> Path:
    """Path to the shared data folder."""
    return DATA_DIR
