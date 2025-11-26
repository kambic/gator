
import asyncio
import json
from rich.console import Group
from rich.live import Live
from rich.text import Text
from loguru import logger
from remote_searcher import RemoteLogSearcher



class AsyncJobRunner:
    def __init__(self, job_configs, max_concurrent=3, output_file="ssh_grep_results.json", include_raw_output=False):
        self.job_configs = job_configs
        self.num_jobs = len(job_configs)
        self.progress = [0 for _ in range(self.num_jobs)]
        self.queue = asyncio.Queue()
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.output_file = output_file
        self.include_raw = include_raw_output

        logger.remove()
        logger.add("remote_jobs.log", level="DEBUG")

    async def run(self):
        self.tasks = [
            asyncio.create_task(self._job_wrapper(i, cfg))
            for i, cfg in enumerate(self.job_configs)
        ]

        with Live(self.render_progress(), refresh_per_second=10) as live:
            while not all(t.done() for t in self.tasks):
                live.update(self.render_progress())
                await asyncio.sleep(0.1)

            live.update(self.render_progress())

        await asyncio.gather(*self.tasks)
        logger.success("All SSH grep jobs completed.")

        await self._drain_results()
        self._save_results_to_json(self.output_file)

    async def _job_wrapper(self, job_id: int, config: dict):
        searcher = RemoteLogSearcher(
            host=config["host"],
            log_file=config["log_file"],
            term=config["search_term"],
            result_queue=self.queue,
            semaphore=self.semaphore,
            include_raw=self.include_raw
        )

        for i in range(100):
            await asyncio.sleep(0.01)
            self.progress[job_id] = i

        await searcher.run()
        self.progress[job_id] = 100

    def render_progress(self) -> Group:
        rows = []
        for i, cfg in enumerate(self.job_configs):
            percent = self.progress[i]
            bar = "█" * (percent // 4) + "-" * ((100 - percent) // 4)
            host = cfg["host"]
            term = cfg["search_term"]
            text = Text(f"[{host}] '{term}': [{bar}] {percent}%")
            rows.append(text)
        return Group(*rows)

    async def _drain_results(self):
        while not self.queue.empty():
            item = await self.queue.get()
            self.results.append(item)

    def _save_results_to_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        logger.success(f"Results saved to {filepath}")
