"""Command Line Interface (CLI) handler for RenFrame."""

import argparse
from renframe import __version__

def main() -> None:
	parser = argparse.ArgumentParser(
		prog="renframe",
		description="Modern UI transpiler and layout framework for Ren'Py.",
		epilog="For more information, check project documentation.")

	parser.add_argument(
			"--version",
			action="version",
			version=f"%(prog)s {__version__}")
	parser.parse_args()
