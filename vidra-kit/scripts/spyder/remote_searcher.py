from fabric import Connection
from loguru import logger
import asyncio

class RemoteLogSearcher:
    def __init__(self, host: str, log_file: str, term: str, result_queue: asyncio.Queue, semaphore: asyncio.Semaphore, include_raw: bool):
        self.host = host
        self.log_file = log_file
        self.term = term
        self.queue = result_queue
        self.semaphore = semaphore
        self.include_raw = include_raw

    async def run(self):
        async with self.semaphore:
            try:
                logger.debug(f"Connecting to {self.host}")
                async with Connection(self.host) as conn:
                    cmd = f"grep '{self.term}' {self.log_file} || true"
                    result = await conn.run(cmd, hide=True)

                    output = result.stdout.strip()
                    lines = output.splitlines()
                    match_count = len(lines)

                    logger.success(f"Grep complete on {self.host} — {match_count} matches")

                    result_entry = {
                        "host": self.host,
                        "term": self.term,
                        "match_count": match_count,
                    }

                    if self.include_raw:
                        result_entry["output"] = lines  # save as list of lines

                    await self.queue.put(result_entry)

            except Exception as e:
                logger.error(f"Error on {self.host}: {e}")
                await self.queue.put({
                    "host": self.host,
                    "term": self.term,
                    "match_count": 0,
                    "error": str(e)
                })
