import random
from datetime import datetime, timedelta
from loguru import logger


class ActivityPlanner:
    def __init__(self):
        # Вероятности
        self.skip_day_chance = 0.25        # 25% — вообще ничего не делать
        self.light_day_chance = 0.35       # 35% — лёгкий день
        self.full_day_chance = 0.40        # 40% — активный день

        # Количество действий
        self.light_day_tx_range = (1, 2)
        self.full_day_tx_range = (5, 12)

        # Паузы между днями
        self.pause_days_after_full = (1, 2)
        self.pause_days_after_light = (0, 1)

    def should_work_today(self) -> bool:
        roll = random.random()

        if roll < self.skip_day_chance:
            logger.info('Planner: skip day (no activity)')
            return False

        logger.info('Planner: active day')
        return True

    def get_day_type(self) -> str:
        roll = random.random()

        if roll < self.light_day_chance:
            return 'LIGHT'
        return 'FULL'

    def get_transactions_count(self, day_type: str) -> int:
        if day_type == 'LIGHT':
            return random.randint(*self.light_day_tx_range)
        return random.randint(*self.full_day_tx_range)

    def get_pause_days_after(self, day_type: str) -> int:
        if day_type == 'LIGHT':
            return random.randint(*self.pause_days_after_light)
        return random.randint(*self.pause_days_after_full)

