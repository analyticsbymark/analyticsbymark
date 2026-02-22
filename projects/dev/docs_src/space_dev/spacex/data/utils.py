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

import pandas as pd


# Resolve path to the existing database module without modifying it
_DATABASE_DIR = Path(__file__).resolve().parent.parent.parent / "database"
_CACHE_DIR = Path(__file__).resolve().parent
_CACHE_FILE = _CACHE_DIR / "spacex_launches.csv"

# SpaceX Launch Service Provider ID in Launch Library 2
_SPACEX_LSP_ID = 121


def _fetch_from_api() -> pd.DataFrame:
    """
    Fetch SpaceX launch data from the LL2 API using the existing
    get_agency_launch_data() function from the database module.

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
        from tutorial_001 import (
            LL2Settings,
            LL2Client,
            get_agency_launch_data,
        )

        settings = LL2Settings()
        client = LL2Client(settings)

        # get_agency_launch_data defaults to lsp__id=121 (SpaceX)
        agency_launches = get_agency_launch_data(client=client)

        # Convert AgencyLaunchData pydantic models to flat dicts
        df = pd.DataFrame([launch.model_dump() for launch in agency_launches])

        if not df.empty:
            # Parse datetime columns
            for col in ["net", "window_start", "window_end", "last_updated"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], utc=True)

            # Derive year/month from net for time-series analysis
            if "net" in df.columns:
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
        pd.DataFrame with columns including:
            launch_name, net, launch_status, launch_status_abbrev,
            operator_name, mission_name, mission_type, mission_description,
            mission_owner_primary_name, program_names,
            rocket_full_name, rocket_name, rocket_family,
            launchpad_name, launchpad_location_name, launchpad_country,
            year, month, and more.

    Example:
        >>> from data.utils import get_spacex_data
        >>> df = get_spacex_data()
        >>> print(df.shape)
    """
    if not force_refresh and _CACHE_FILE.exists():
        df = pd.read_csv(_CACHE_FILE, parse_dates=["net", "window_start", "window_end", "last_updated"])
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
    print(f"\nDate range: {df['net'].min()} to {df['net'].max()}")
    print(f"\nShape: {df.shape}")
    print(f"\nMission types:\n{df['mission_type'].value_counts()}")
    print(f"\nRockets:\n{df['rocket_name'].value_counts()}")
    print(f"\nLaunch statuses:\n{df['launch_status'].value_counts()}")
