"""Entry point: delegate to the shell, and do nothing else."""

from decision_queue_validator.shell import main

if __name__ == "__main__":
    raise SystemExit(main())
