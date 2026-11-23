"""Command-line interface for batch incident triage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from .batch import load_incidents
from .enrichment import enrich_incident
from .triage import triage_incident


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Triage data incidents with Jev")
    parser.add_argument("path", type=Path, help="JSON file containing an incident list")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    try:
        incidents = load_incidents(args.path)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Invalid incident batch: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    decisions = [
        triage_incident(enrich_incident(item)).as_dict()
        for item in incidents
    ]
    print(json.dumps(decisions, indent=2))


if __name__ == "__main__":
    main()
