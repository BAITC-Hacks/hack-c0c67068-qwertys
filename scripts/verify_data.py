"""Verify official CSVs locally without copying their contents into the repository."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path)
    args = parser.parse_args()
    manifest = Path(__file__).resolve().parents[1] / "coordination" / "DATA_MANIFEST.json"
    failed = False
    for item in json.loads(manifest.read_text(encoding="utf-8-sig")):
        path = args.data_dir / item["filename"]
        if not path.is_file():
            print(f"MISSING: {item['filename']}")
            failed = True
            continue
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        ok = digest.lower() == item["sha256"].lower() and path.stat().st_size == item["bytes"]
        print(f"{'OK' if ok else 'MISMATCH'}: {item['filename']} sha256={digest}")
        failed |= not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
