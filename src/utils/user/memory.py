from collections import defaultdict
from datetime import datetime, timedelta


class MemoryManager:
    def __init__(self):
        self.last_chain = {}
        self.last_bridge_day = {}
        self.recent_tasks = defaultdict(list)

    # ===== CHAINS =====
    def remember_chain(self, wallet: str, chain: str):
        self.last_chain[wallet] = chain

    def get_last_chain(self, wallet: str):
        return self.last_chain.get(wallet)

    # ===== BRIDGES =====
    def remember_bridge(self, wallet: str):
        self.last_bridge_day[wallet] = datetime.utcnow()

    def can_bridge_today(self, wallet: str, cooldown_days: int = 2) -> bool:
        last = self.last_bridge_day.get(wallet)
        if not last:
            return True
        return datetime.utcnow() - last > timedelta(days=cooldown_days)

    # ===== TASKS =====
    def remember_task(self, wallet: str, task: str, limit: int = 5):
        self.recent_tasks[wallet].append(task)
        self.recent_tasks[wallet] = self.recent_tasks[wallet][-limit:]

    def was_task_recent(self, wallet: str, task: str) -> bool:
        return task in self.recent_tasks[wallet]

