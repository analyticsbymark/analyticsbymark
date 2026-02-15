"""
SpaceX data utility for tutorial consumption.

Provides a single clean interface: get_spacex_data() -> pd.DataFrame

Cache-first architecture:
1. If a local CSV cache exists, load from it (fast, no network)
2. Otherwise, fetch from the Launch Library 2 API via the existing LL2Client
3. Save to CSV for future runs

All tutorials import data the same way:
    from data.utils import get_spacex_data
    df = get_spacex_data()
"""

import sys
from pathlib import Path
from typing import Optional

import pandas as pd


# Resolve path to the existing database module without modifying it
_DATABASE_DIR = Path(__file__).resolve().parent.parent.parent / "database"
_CACHE_DIR = Path(__file__).resolve().parent
_CACHE_FILE = _CACHE_DIR / "spacex_launches.csv"

# SpaceX Launch Service Provider ID in Launch Library 2
_SPACEX_LSP_ID = 121


def _fetch_from_api() -> pd.DataFrame:
    """
    Fetch SpaceX launch data from the LL2 API using the existing LL2Client.

    Returns a flat DataFrame with one row per launch.
    """
    # Temporarily add the database directory to sys.path so we can import
    # the existing LL2Client without modifying any original files
    db_dir_str = str(_DATABASE_DIR)
    added_to_path = False
    if db_dir_str not in sys.path:
        sys.path.insert(0, db_dir_str)
        added_to_path = True

    try:
        from tutorial_001 import LL2Settings, LL2Client, safe_get

        settings = LL2Settings()
        client = LL2Client(settings)

        params = {
            "ordering": "-net",
            "lsp__id": _SPACEX_LSP_ID,
            "limit": 100,
        }

        raw_launches = client.get_results(
            settings.EP_LAUNCHES, params=params
        )

        rows = []
        for launch in raw_launches:
            rows.append(
                {
                    "launch_name": safe_get(launch, "name"),
                    "net": safe_get(launch, "net"),
                    "launch_status": safe_get(launch, "status", "name"),
                    "mission_name": safe_get(launch, "mission", "name"),
                    "mission_type": safe_get(launch, "mission", "type"),
                    "rocket_name": safe_get(
                        launch, "rocket", "configuration", "name"
                    ),
                    "launchpad_name": safe_get(launch, "pad", "name"),
                }
            )

        df = pd.DataFrame(rows)

        # Parse dates and derive year/month columns
        if not df.empty and "net" in df.columns:
            df["net"] = pd.to_datetime(df["net"], utc=True)
            df["year"] = df["net"].dt.year
            df["month"] = df["net"].dt.month

        return df

    finally:
        if added_to_path and db_dir_str in sys.path:
            sys.path.remove(db_dir_str)


def get_spacex_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load SpaceX launch data as a clean, flat DataFrame.

    Uses a local CSV cache for speed. Pass force_refresh=True to
    re-fetch from the LL2 API.

    Returns:
        pd.DataFrame with columns:
            launch_name, net, launch_status, mission_name, mission_type,
            rocket_name, launchpad_name, year, month

    Example:
        >>> from data.utils import get_spacex_data
        >>> df = get_spacex_data()
        >>> print(df.shape)
    """
    if not force_refresh and _CACHE_FILE.exists():
        df = pd.read_csv(_CACHE_FILE, parse_dates=["net"])
        return df

    df = _fetch_from_api()

    # Save to cache
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(_CACHE_FILE, index=False)

    return df


if __name__ == "__main__":
    df = get_spacex_data()
    print(f"Loaded {len(df)} SpaceX launches")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['net'].min()} to {df['net'].max()}")
    print(df.head())
