import random
from datetime import datetime, timedelta
from loguru import logger
from src.utils.data.bridges import BRIDGES

class ActivityPlanner:
    def __init__(self):
        # Вероятности
        self.skip_day_chance = 0.15        # 25% — вообще ничего не делать
        self.light_day_chance = 0.35       # 35% — лёгкий день
        self.full_day_chance = 0.50        # 40% — активный день

        # Количество действий
        self.light_day_tx_range = (3, 5)
        self.full_day_tx_range = (6, 12)

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

        base_skip = self.skip_day_chance

        if self.personality == 'LAZY':
            base_skip += 0.25
        elif self.personality == 'ACTIVE':
            base_skip -= 0.15

        adjusted_skip = base_skip / modifier
        adjusted_skip = min(max(adjusted_skip, 0.05), 0.9)

        if roll < adjusted_skip:
            logger.info(f'Planner: skip day ({self.personality})')
            return False

        logger.info(f'Planner: active day ({self.personality})')
        return True
        
    def get_day_type(self) -> str:
        roll = random.random()

        if roll < self.light_day_chance:
            return 'LIGHT'
        return 'FULL'

    def choose_chain(self, wallet_id):
        chain = self.get_chain_for_today()
        return chain

    def get_transactions_count(self, day_type: str) -> int:
        # Всегда рандом 2–4 бриджa, игнорируем day_type и modifier
        tx_count = random.randint(2, 4)

        # Влияние личности (опционально, можно оставить)
        if self.personality == 'ACTIVE':
            tx_count += random.randint(1, 2)
        elif self.personality == 'LAZY':
            tx_count = max(2, tx_count - 1)

        # Weekend modifier — отключаем (или оставляем, если хочешь)
        # modifier = self.get_weekday_modifier()  # ← закомментируй, если нужно
        # tx_count = int(tx_count * modifier)

        logger.info(f"Planner: transactions count → {tx_count} (personality: {self.personality})")
        return max(2, tx_count)  # ← минимум 2, чтобы никогда не было 1

    def get_pause_days_after(self, day_type: str) -> int:
        if day_type == 'LIGHT':
            return random.randint(*self.pause_days_after_light)
        return random.randint(*self.pause_days_after_full)
        
    def get_chain_for_today(self) -> str:
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

        logger.info(f'Planner: selected chain → {chain}')
        return chain
        
    def is_bridge_day(self, day_type: str) -> bool:
        base_chance = 0.15 if day_type == 'LIGHT' else 0.35

        if self.personality == 'BRIDGE_LOVER':
            base_chance += 0.25
        elif self.personality == 'LAZY':
            base_chance -= 0.10

        return random.random() < max(0.05, min(base_chance, 0.8))

    from src.utils.data.bridges import BRIDGES

    def choose_bridge_target(self, current_chain: str) -> str | None:
        targets = BRIDGES.get(current_chain, [])
        if not targets:
            return None
        return random.choice(targets)

    def get_weekday_modifier(self) -> float:
        """
        Модификатор активности по дню недели
        """
        weekday = datetime.utcnow().weekday()  # 0 = Monday, 6 = Sunday

        if weekday in (5, 6):  # Saturday, Sunday
            logger.info('Planner: weekend detected → lower activity')
            return 0.6

        return 1.0
           
    





