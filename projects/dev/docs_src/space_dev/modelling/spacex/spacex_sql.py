"""
SpaceX Launch Data — SQLModel Database Persistence
====================================================

Builds on spacex.py to teach database basics with real SpaceX data.

This script:
1. Imports the validated SpaceXLaunch Pydantic model from spacex.py
2. Extends it into a SQLModel table with an auto-increment primary key
3. Creates a SQLite database and inserts validated launch data
4. Demonstrates querying with SQLModel's select()

Usage:
    python spacex_sql.py            # Create DB, insert, and query
    python spacex_sql.py --refresh  # Re-fetch data from API first
"""

# ──────────────────────────────────────────────────────────────────────
# Section 1: Imports
#
# We import SpaceXLaunch from spacex.py (same directory) to reuse
# the validated SQLModel schema. We inherit from it to create a
# database table class.
# ──────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

import pandas as pd
from sqlmodel import Field, Session, SQLModel, create_engine, select

from spacex import SpaceXLaunch, get_spacex_data


# ──────────────────────────────────────────────────────────────────────
# Section 2: SQLModel Table
#
# SpaceXLaunch is already a SQLModel, so we just need to:
#   1. Inherit from it
#   2. Set table=True to mark it as a database table
#   3. Add an auto-increment primary key
#
# Every field from SpaceXLaunch becomes a database column automatically.
# ──────────────────────────────────────────────────────────────────────

class SpaceXLaunchRow(SpaceXLaunch, table=True):
    """Database table for SpaceX launches. Inherits all fields from SpaceXLaunch."""
    __tablename__ = "spacex_launches"

    id: int | None = Field(default=None, primary_key=True)


# ──────────────────────────────────────────────────────────────────────
# Section 3: Database Setup
#
# SQLite stores the entire database in a single file — no server needed.
# create_engine() connects to the database file.
# create_all() creates tables from our SQLModel definitions.
# ──────────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).resolve().parent / "spacex.db"
engine = create_engine(f"sqlite:///{DB_PATH}")


# ──────────────────────────────────────────────────────────────────────
# Section 4: Write Data
#
# Load CSV data and insert into the database:
# 1. Iterate each row from the DataFrame
# 2. Validate through the Pydantic model
# 3. Insert via a SQLModel Session
#
# The Session acts like a transaction — changes are only saved when
# you call session.commit().
# ──────────────────────────────────────────────────────────────────────

def insert_launches(df: pd.DataFrame):
    """Insert launch data from a DataFrame into the database."""
    with Session(engine) as session:
        for _, row in df.iterrows():
            # Drop derived columns (year/month) that aren't in the Pydantic model,
            # and convert NaN to None for Pydantic compatibility
            row_dict = row.to_dict()
            row_dict.pop("year", None)
            row_dict.pop("month", None)
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}

            db_row = SpaceXLaunchRow(**row_dict)
            session.add(db_row)

        session.commit()


# ──────────────────────────────────────────────────────────────────────
# Section 5: Query Data & Main
#
# SQLModel's select() creates type-safe queries. Combined with
# session.exec(), it returns Python objects you can work with directly.
#
# This section demonstrates the most common query patterns:
# - Select all rows
# - Filter with .where()
# - Order and limit results
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    refresh = "--refresh" in sys.argv

    # Create tables and load data
    SQLModel.metadata.create_all(engine)
    df = get_spacex_data(force_refresh=refresh)
    insert_launches(df)
    print(f"Inserted {len(df)} launches into {DB_PATH.name}")

    with Session(engine) as session:

        # Query 1: Count all launches
        all_launches = session.exec(select(SpaceXLaunchRow)).all()
        print(f"\nTotal launches in database: {len(all_launches)}")

        # Query 2: Filter by rocket name
        print("\nLaunches by rocket:")
        for rocket in ("Falcon 9", "Falcon Heavy", "Falcon 1", "Starship"):
            matches = session.exec(
                select(SpaceXLaunchRow).where(SpaceXLaunchRow.rocket_name == rocket)
            ).all()
            if matches:
                print(f"  {rocket}: {len(matches)}")

        # Query 3: Count by status
        print("\nLaunches by status:")
        for launch in all_launches:
            status = launch.launch_status_abbrev or "Unknown"
        counts: dict[str, int] = {}
        for launch in all_launches:
            status = launch.launch_status_abbrev or "Unknown"
            counts[status] = counts.get(status, 0) + 1
        for status, count in sorted(counts.items()):
            print(f"  {status}: {count}")

        # Query 4: Most recent completed launches (order + filter + limit)
        print("\n10 most recent completed launches:")
        recent = session.exec(
            select(SpaceXLaunchRow)
            .where(SpaceXLaunchRow.launch_status_abbrev.in_(["Success", "Failure", "Partial Failure"]))
            .order_by(SpaceXLaunchRow.net.desc())
            .limit(10)
        ).all()
        for launch in recent:
            net_str = launch.net.strftime("%Y-%m-%d") if launch.net else "TBD"
            print(f"  {net_str}  {launch.launch_name}  [{launch.launch_status_abbrev}]")
