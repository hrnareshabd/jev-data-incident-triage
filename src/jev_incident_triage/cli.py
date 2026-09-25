"""Command-line interface for batch incident triage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from .enrichment import enrich_incident
from .models import Incident
from .triage import triage_incident


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Triage data incidents with Jev")
    parser.add_argument("path", type=Path, help="JSON file containing an incident list")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    incidents = json.loads(args.path.read_text(encoding="utf-8"))
    decisions = [
        triage_incident(enrich_incident(Incident.from_dict(item))).as_dict()
        for item in incidents
    ]
    print(json.dumps(decisions, indent=2))


if __name__ == "__main__":
    main()
