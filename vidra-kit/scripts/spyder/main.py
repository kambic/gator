
import argparse
from remote_config import remote_hosts
from async_runner import AsyncJobRunner

import asyncio


def parse_args():
    parser = argparse.ArgumentParser(description="Run remote grep over SSH with term filter")
    parser.add_argument(
        "--term",
        type=str,
        required=True,
        help="Search term to grep for in remote logs",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Maximum number of concurrent SSH connections",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="ssh_grep_results.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Include raw grep output in JSON results",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    job_configs = [
        {**job, "search_term": args.term}
        for job in remote_hosts
    ]

    runner = AsyncJobRunner(
        job_configs,
        max_concurrent=args.concurrency,
        output_file=args.out,
        include_raw_output=args.raw
    )
    asyncio.run(runner.run())
