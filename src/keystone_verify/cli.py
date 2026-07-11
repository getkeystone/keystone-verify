"""CLI for Keystone Verify.

Usage:
  keystone-verify run --profile profiles/engage.json --cases cases.jsonl
  keystone-verify run --profile profiles/counsel.json --cases cases.jsonl --output results/
"""

from __future__ import annotations

import logging

import click

from keystone_verify import __version__
from keystone_verify.loader import load_cases, load_profile
from keystone_verify.reporter import write_artifacts
from keystone_verify.runner import run

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@click.group()
@click.version_option(__version__)
def main():
    """Keystone Verify: evaluation harness for governed AI systems."""
    pass


@main.command()
@click.option(
    "--profile", "-p",
    required=True,
    type=click.Path(exists=True),
    help="Path to target profile JSON.",
)
@click.option(
    "--cases", "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to eval cases JSONL.",
)
@click.option(
    "--output", "-o",
    default="results",
    type=click.Path(),
    help="Output directory for sealed artifacts.",
)
@click.option(
    "--run-id",
    default=None,
    help="Override the auto-generated run ID.",
)
def run_cmd(profile: str, cases: str, output: str, run_id: str | None):
    """Run evaluation cases against a target endpoint."""
    p = load_profile(profile)
    c = load_cases(cases)

    if not c:
        click.echo("No cases loaded. Check the cases file.")
        return

    summary, results = run(p, c, run_id=run_id)
    write_artifacts(summary, results, output)


# Alias so `keystone-verify run` works
main.add_command(run_cmd, name="run")
