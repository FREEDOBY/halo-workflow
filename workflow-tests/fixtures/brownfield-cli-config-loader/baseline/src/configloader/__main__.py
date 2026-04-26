"""Module entry point: python -m configloader <config.json>."""
import sys

from configloader.loader import load_config


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: python -m configloader <config.json>", file=sys.stderr)
        return 1
    try:
        cfg = load_config(argv[0])
    except FileNotFoundError:
        print(f"File not found: {argv[0]}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Invalid config: {e}", file=sys.stderr)
        return 3
    for k, v in cfg.items():
        print(f"{k}={v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
