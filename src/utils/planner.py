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
        self.personality = None

    def assign_wallet_personality(self, wallet_id: str) -> str:
        """
        Закрепляем характер за кошельком НАВСЕГДА
        """
        random.seed(wallet_id)

        personalities = [
            'LAZY',        # часто пропускает дни
            'NORMAL',      # обычный
            'ACTIVE',      # много действий
            'BRIDGE_LOVER' # часто мосты
        ]

        personality = random.choice(personalities)
        logger.info(f'Planner: wallet personality → {personality}')
        return personality

    def should_work_today(self) -> bool:
        modifier = self.get_weekday_modifier()
        roll = random.random()

        adjusted_skip = self.skip_day_chance / modifier

        if roll < adjusted_skip:
            logger.info('Planner: skip day (weekly behavior)')
            return False

        logger.info('Planner: active day')
        return True
        
    def get_day_type(self) -> str:
        roll = random.random()

        if roll < self.light_day_chance:
            return 'LIGHT'
        return 'FULL'

    def get_transactions_count(self, day_type: str) -> int:
        modifier = self.get_weekday_modifier()

        if day_type == 'LIGHT':
            base = random.randint(*self.light_day_tx_range)
        else:
            base = random.randint(*self.full_day_tx_range)

        tx_count = int(base * modifier)
        return max(1, tx_count)

    def get_pause_days_after(self, day_type: str) -> int:
        if day_type == 'LIGHT':
            return random.randint(*self.pause_days_after_light)
        return random.randint(*self.pause_days_after_full)
        
    def get_chain_for_today(self) -> str:
        """
        Выбор сети на день (multi-chain поведение)
        """
        weights = {
            'BASE': 40,
            'OPTIMISM': 20,
            'ARBITRUM': 20,
            'LINEA': 15,
            'ETHEREUM': 5
        }

        chain = random.choices(
            population=list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]

        logger.info(f'Planner: selected chain for today → {chain}')
        return chain

    def is_bridge_day(self, day_type: str) -> bool:
        if day_type == 'FULL':
            return random.random() < 0.35
        return random.random() < 0.15

    def get_weekday_modifier(self) -> float:
        """
        Модификатор активности по дню недели
        """
        weekday = datetime.utcnow().weekday()  # 0 = Monday, 6 = Sunday

        if weekday in (5, 6):  # Saturday, Sunday
            logger.info('Planner: weekend detected → lower activity')
            return 0.6

        return 1.0
           
    





