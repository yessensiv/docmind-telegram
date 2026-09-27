"""Small local CLI that only prints a route."""

import argparse

from .models import Task, TaskKind
from .router import route_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline model router")
    parser.add_argument("description")
    parser.add_argument("--kind", choices=[kind.value for kind in TaskKind], default="simple")
    parser.add_argument("--tokens", type=int, default=1000)
    parser.add_argument("--operations", type=int, default=1)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()

    route = route_task(
        Task(args.description, TaskKind(args.kind), args.tokens, args.operations),
        confirmed=args.confirm,
    )
    print(f"model={route.model.value}")
    print(f"estimated_tokens={route.estimated_tokens}")
    print(f"requires_confirmation={route.requires_confirmation}")
    print(f"reason={route.reason}")


if __name__ == "__main__":
    main()
