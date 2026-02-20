# AGENT_INDEX.md --- Master Tutorial Index (Tier 1)

> This file is maintained by the `summarise_for_agents` agent.
> It provides a single lookup table for all tutorial curiosities across all datasets.
> Last updated: 2026-02-21

## Curiosities

| Curiosity | Dataset | Data Source | Kirk Chapters | Difficulty | Status | Tutorials | Images | Interactive | Link |
|---|---|---|---|---|---|---|---|---|---|
| launch_cadence | spacex | space_dev | 4, 5, 6, 7, 8, 9, 10, 11 | beginner | complete | 5 | 19 | yes | [space_dev/spacex/launch_cadence/](space_dev/spacex/launch_cadence/) |
| launch_reliability | spacex | space_dev | 4, 5, 6, 7, 8, 9, 10, 11 | beginner | complete | 5 | 16 | yes | [space_dev/spacex/launch_reliability/](space_dev/spacex/launch_reliability/) |
| customer_concentration | spacex | space_dev | 4, 5, 6, 7, 8, 9, 10, 11 | beginner | complete | 5 | 18 | yes | [space_dev/spacex/customer_concentration/](space_dev/spacex/customer_concentration/) |

## How to Use This Index

- **AI agents:** Parse the table above to find tutorials by dataset, difficulty, or Kirk chapter. Each curiosity folder contains an `AGENT_SUMMARY.md` with full details (10 sections covering question, dataset, progression, decisions, code patterns, dependencies, images, tests, domain transfer, and metadata).
- **Humans:** Click the link column to navigate to a curiosity folder.
- **Adding a curiosity:** Run the `summarise_for_agents` agent after completing a tutorial series. It will update this file automatically.

## Data Sources

| Data Source | Category Index | Datasets | Curiosities |
|---|---|---|---|
| space_dev | [SPACE_DEV_INDEX.md](space_dev/SPACE_DEV_INDEX.md) | spacex | launch_cadence, launch_reliability, customer_concentration |

## Status Legend

| Status | Meaning |
|---|---|
| brief | Curiosity question defined, no tutorials yet |
| scaffold | Folder structure created, tutorials not yet written |
| in_progress | Some tutorials complete, series not finished |
| complete | All tutorials written, tested, and verified working |

## Kirk Chapter Coverage

| Chapter | Topic | Curiosities Using It |
|---|---|---|
| Ch 4 | Working with Data | launch_cadence, launch_reliability, customer_concentration |
| Ch 5 | Editorial Thinking | launch_cadence, launch_reliability, customer_concentration |
| Ch 6 | Design Solutions | launch_cadence, launch_reliability, customer_concentration |
| Ch 7 | Data Representation | launch_cadence, launch_reliability, customer_concentration |
| Ch 8 | Interactivity | launch_cadence, launch_reliability, customer_concentration |
| Ch 9 | Annotation | launch_cadence, launch_reliability, customer_concentration |
| Ch 10 | Color | launch_cadence, launch_reliability, customer_concentration |
| Ch 11 | Composition | launch_cadence, launch_reliability, customer_concentration |
