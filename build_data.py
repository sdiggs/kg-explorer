#!/usr/bin/env python3
"""
build_data.py  —  Bundles approved JSON files into data.json for KG Explorer.

2026-04-04: S. Diggs with Claude.ai 

Usage:
    python build_data.py                    # bundle everything in approved/
    python build_data.py --anonymize        # strip names & contact info
    python build_data.py --check            # just report what would be bundled

Directory layout expected:
    approved/        ← JSON files interviewees have OKed for public display
    private/         ← JSON files NOT for public hosting (drag-drop only)
    data.json        ← OUTPUT: auto-generated, committed to repo
    index.html       ← the KG explorer

The approved/ folder is committed to the repo.
The private/ folder should be in .gitignore.
"""

import json, glob, os, sys, re, datetime, argparse

def strip_comments(s):
    """State-machine JSON comment stripper (skips // inside strings)."""
    out, in_str, i = [], False, 0
    while i < len(s):
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\": out.append(s[i+1] if i+1<len(s) else ""); i += 1
            elif c == '"': in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif c == "/" and i+1 < len(s) and s[i+1] == "/":
            while i < len(s) and s[i] != "\n": i += 1
            continue
        elif c == "/" and i+1 < len(s) and s[i+1] == "*":
            i += 2
            while i < len(s) and not (s[i] == "*" and i+1<len(s) and s[i+1] == "/"): i += 1
            i += 1
        else:
            out.append(c)
        i += 1
    return "".join(out)

def anonymize(data):
    """Strip identifying fields from people records."""
    data = json.loads(json.dumps(data))  # deep copy
    for p in data.get("people", []):
        p["name"] = "Anonymous"
        p["orcid"] = ""
        p.pop("contactInformation", None)
        p.pop("reputation", None)
        p.pop("gsLevel", None)
        # Nested schemas
        if "basicInformation" in p:
            p["basicInformation"]["name"] = "Anonymous"
        if "contactInformation" in p:
            p["contactInformation"] = {}
    return data

def load_file(path, do_anon=False):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(strip_comments(raw))
    if do_anon:
        data = anonymize(data)
    people = data.get("people", [])
    datasets = data.get("datasets", [])
    return {
        "filename": os.path.basename(path),
        "people_count": len(people),
        "dataset_count": len(datasets),
        "data": data,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--anonymize", action="store_true", help="Strip names and contact info")
    parser.add_argument("--check",     action="store_true", help="Dry run — report only")
    parser.add_argument("--dir",       default="approved",  help="Source directory (default: approved/)")
    args = parser.parse_args()

    src_dir = args.dir
    if not os.path.isdir(src_dir):
        print(f"ERROR: directory \"{src_dir}\" not found.")
        print(f"Create it and put your approved JSON files there.")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(src_dir, "*.json")))
    if not files:
        print(f"No .json files found in {src_dir}/")
        sys.exit(0)

    print(f"\n{'DRY RUN — ' if args.check else ''}Building data.json from {len(files)} files in {src_dir}/")
    if args.anonymize:
        print("  Mode: ANONYMIZED (names and contacts stripped)")
    else:
        print("  Mode: FULL (names and contacts preserved)")
    print()

    records = []
    total_people, total_datasets = 0, 0
    errors = []

    for path in files:
        name = os.path.basename(path)
        try:
            rec = load_file(path, do_anon=args.anonymize)
            records.append(rec)
            total_people   += rec["people_count"]
            total_datasets += rec["dataset_count"]
            print(f"  OK  {name[:55]:<55}  {rec['people_count']}p  {rec['dataset_count']}ds")
        except Exception as e:
            errors.append((name, str(e)))
            print(f"  ERR {name[:55]:<55}  {e}")

    print()
    print(f"  Total: {len(records)} files, {total_people} people, {total_datasets} datasets")
    if errors:
        print(f"  ERRORS: {len(errors)} files failed — fix before committing")
    print()

    if args.check:
        print("Dry run complete. No files written.")
        return

    bundle = {
        "version": "1.0",
        "built": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "anonymized": args.anonymize,
        "file_count": len(records),
        "people_count": total_people,
        "dataset_count": total_datasets,
        "files": records,
    }

    out_path = "data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Written: {out_path}  ({size_kb:.1f} KB)")
    print()
    print("Next steps:")
    print("  git add data.json index.html")
    print("  git commit -m \"Update KG data bundle\"")
    print("  git push")

if __name__ == "__main__":
    main()
