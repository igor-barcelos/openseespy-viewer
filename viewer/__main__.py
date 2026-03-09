"""CLI entry point: python -m openseespy_viewer model1.py [model2.py ...]"""

import argparse
from .viewer import view


def main():
    parser = argparse.ArgumentParser(
        prog="openseespy-viewer",
        description="Live visual previewer for OpenSeesPy models.",
    )
    parser.add_argument(
        "modelfiles", nargs="+",
        help="One or more OpenSeesPy model files (.py) to visualise.",
    )
    parser.add_argument(
        "--refresh", type=float, default=0.5,
        help="Minimum refresh interval in seconds (default: 0.5).",
    )
    args = parser.parse_args()
    view(*args.modelfiles, min_refresh_interval=args.refresh)


if __name__ == "__main__":
    main()
