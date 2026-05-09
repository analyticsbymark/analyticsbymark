"""
SpaceX Launch Data — Fetch, Validate, Save
===========================================

Self-contained script that:
1. Fetches SpaceX launch data from the Launch Library 2 API
2. Validates each record with a SQLModel schema
3. Saves a flat CSV for downstream analysis

Usage:
    python spacex.py              # Use cached CSV if available
    python spacex.py --refresh    # Force re-fetch from API

Output:
    modelling/spacex/spacex_launches.csv
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from sqlmodel import SQLModel

API_URL = "https://ll.thespacedevs.com/2.3.0/launches/"
SPACEX_LSP_ID = 121
OUTPUT_CSV = Path(__file__).resolve().parent / "spacex_launches.csv"


class SpaceXLaunch(SQLModel):
    """A single SpaceX launch, flattened from the nested API response."""

    launch_uuid: str | None = None
    launch_url: str | None = None
    net: datetime | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None
    last_updated: datetime | None = None
    launch_name: str
    launch_status: str | None = None
    launch_status_id: int | None = None
    launch_status_abbrev: str | None = None
    launch_status_description: str | None = None
    operator_id: int | None = None
    operator_name: str | None = None
    mission_id: int | None = None
    mission_name: str | None = None
    mission_type: str | None = None
    mission_description: str | None = None
    mission_owner_primary_id: int | None = None
    mission_owner_primary_name: str | None = None
    mission_owner_all_ids: str | None = None
    mission_owner_all_names: str | None = None
    program_names: str | None = None
    image_thumbnail: str | None = None
    rocket_full_name: str | None = None
    rocket_variant: str | None = None
    rocket_name: str | None = None
    rocket_family: str | None = None
    launchpad_id: int | None = None
    launchpad_name: str | None = None
    launchpad_description: str | None = None
    launchpad_map_url: str | None = None
    launchpad_latitude: float | None = None
    launchpad_longitude: float | None = None
    launchpad_location_name: str | None = None
    launchpad_country: str | None = None


def safe_get(obj, *keys, default=None):
    """Safely navigate nested dicts and lists without raising KeyError or IndexError."""
    current = obj
    for key in keys:
        if current is None:
            return default
        if isinstance(key, int):
            if isinstance(current, list) and len(current) > key:
                current = current[key]
            else:
                return default
        else:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
    return current


def fetch_all_pages(url: str, params: dict | None = None) -> list[dict]:
    """Fetch all results from a paginated LL2 endpoint."""
    headers = {"User-Agent": "SpaceXTutorial/1.0", "Accept": "application/json"}
    all_results: list[dict] = []

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    all_results.extend(data.get("results", []))
    next_url = data.get("next")

    print(f"  Page 1: {len(data.get('results', []))} results (total: {data.get('count', '?')})")

    page = 2
    while next_url:
        resp = requests.get(next_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        all_results.extend(data.get("results", []))
        next_url = data.get("next")
        print(f"  Page {page}: {len(data.get('results', []))} results")
        page += 1

    return all_results


def parse_launch(launch_dict: dict) -> SpaceXLaunch:
    """Transform a raw API launch dict into a validated SpaceXLaunch model."""
    agencies = list(safe_get(launch_dict, "mission", "agencies") or [])
    for p in safe_get(launch_dict, "program") or []:
        agencies.extend(safe_get(p, "agencies") or [])
    owners = list(dict.fromkeys(a["id"] for a in agencies if "id" in a))
    owner_lookup = {a["id"]: a for a in agencies if "id" in a}

    programs = safe_get(launch_dict, "program") or []
    program_names = "; ".join(dict.fromkeys(
        safe_get(p, "name") for p in programs if safe_get(p, "name")
    ))

    return SpaceXLaunch(
        launch_uuid=safe_get(launch_dict, "id"),
        launch_url=safe_get(launch_dict, "url"),
        net=safe_get(launch_dict, "net"),
        window_start=safe_get(launch_dict, "window_start"),
        window_end=safe_get(launch_dict, "window_end"),
        last_updated=safe_get(launch_dict, "last_updated"),
        launch_name=safe_get(launch_dict, "name"),
        launch_status=safe_get(launch_dict, "status", "name"),
        launch_status_id=safe_get(launch_dict, "status", "id"),
        launch_status_abbrev=safe_get(launch_dict, "status", "abbrev"),
        launch_status_description=safe_get(launch_dict, "status", "description"),
        operator_id=safe_get(launch_dict, "launch_service_provider", "id"),
        operator_name=safe_get(launch_dict, "launch_service_provider", "name"),
        mission_id=safe_get(launch_dict, "mission", "id"),
        mission_name=safe_get(launch_dict, "mission", "name"),
        mission_type=safe_get(launch_dict, "mission", "type"),
        mission_description=safe_get(launch_dict, "mission", "description"),
        mission_owner_primary_id=owners[0] if owners else None,
        mission_owner_primary_name=safe_get(owner_lookup.get(owners[0]), "name") if owners else None,
        mission_owner_all_ids=";".join(str(i) for i in owners) if owners else None,
        mission_owner_all_names=";".join(safe_get(owner_lookup[i], "name") for i in owners if safe_get(owner_lookup[i], "name")) if owners else None,
        program_names=program_names or None,
        image_thumbnail=safe_get(launch_dict, "image", "thumbnail_url"),
        rocket_full_name=safe_get(launch_dict, "rocket", "configuration", "full_name"),
        rocket_variant=safe_get(launch_dict, "rocket", "configuration", "variant"),
        rocket_name=safe_get(launch_dict, "rocket", "configuration", "name"),
        rocket_family=safe_get(launch_dict, "rocket", "configuration", "families", 0, "name"),
        launchpad_id=safe_get(launch_dict, "pad", "id"),
        launchpad_name=safe_get(launch_dict, "pad", "name"),
        launchpad_description=safe_get(launch_dict, "pad", "description"),
        launchpad_map_url=safe_get(launch_dict, "pad", "map_url"),
        launchpad_latitude=safe_get(launch_dict, "pad", "latitude"),
        launchpad_longitude=safe_get(launch_dict, "pad", "longitude"),
        launchpad_location_name=safe_get(launch_dict, "pad", "location", "name"),
        launchpad_country=safe_get(launch_dict, "pad", "country", "alpha_3_code"),
    )


def get_spacex_data(force_refresh: bool = False) -> pd.DataFrame:
    """Load SpaceX launch data with cache-first strategy."""
    if not force_refresh and OUTPUT_CSV.exists():
        print(f"Loading cached data from {OUTPUT_CSV}")
        return pd.read_csv(
            OUTPUT_CSV,
            parse_dates=["net", "window_start", "window_end", "last_updated"],
        )

    print("Fetching SpaceX launches from Launch Library 2 API...")
    raw_launches = fetch_all_pages(API_URL, params={
        "ordering": "-net",
        "lsp__id": SPACEX_LSP_ID,
        "limit": 100,
    })
    print(f"Fetched {len(raw_launches)} launches")

    launches = [parse_launch(raw) for raw in raw_launches]
    df = pd.DataFrame([launch.model_dump() for launch in launches])

    for col in ("net", "window_start", "window_end", "last_updated"):
        df[col] = pd.to_datetime(df[col], utc=True)
    df["year"] = df["net"].dt.year
    df["month"] = df["net"].dt.month

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} launches to {OUTPUT_CSV}")

    return df


if __name__ == "__main__":
    refresh = "--refresh" in sys.argv
    df = get_spacex_data(force_refresh=refresh)

    print(f"\n{'='*60}")
    print(f"SpaceX Launch Dataset Summary")
    print(f"{'='*60}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"\nDate range: {df['net'].min()} to {df['net'].max()}")
    print(f"\nRockets:\n{df['rocket_name'].value_counts().to_string()}")
    print(f"\nLaunch statuses:\n{df['launch_status_abbrev'].value_counts().to_string()}")
    print(f"\nMission types:\n{df['mission_type'].value_counts().head(10).to_string()}")
