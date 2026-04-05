# KG Explorer

Interactive knowledge graph for climate data assets, datasets, and people.

## Live tool
https://sdiggs.github.io/[repo-name]/

## How it works

The tool auto-loads `data.json` (pre-built bundle of approved records) when the page opens.
Users can also drag-and-drop additional JSON files to supplement the shared data.

## Repository layout

```
index.html          ← the KG explorer (this file)
data.json           ← pre-built bundle of approved records (auto-loaded)
build_data.py       ← script to rebuild data.json from source files
approved/           ← JSON files approved for public hosting (committed)
private/            ← JSON files NOT for public hosting (.gitignored)
README.md
.gitignore
```

## Updating the data

1. Put approved JSON files in `approved/`
2. Run: `python build_data.py`
3. Commit and push `data.json`

```bash
python build_data.py            # full names (for approved-consent records)
python build_data.py --anonymize  # strip names/contacts (for mixed-consent records)
python build_data.py --check      # dry run, no files written
```

## Privacy tiers

| Tier | Where | Who sees it |
|---|---|---|
| Public (full) | `approved/` → `data.json` | Everyone |
| Public (anonymized) | `approved/` → `data.json --anonymize` | Everyone (names stripped) |
| Private | `private/` (.gitignored) | You only, via drag-drop |

## Schema versions supported
v1 (entities/relationships), v2.0, v2.2, v2x (interview-extracted), v3, v4
