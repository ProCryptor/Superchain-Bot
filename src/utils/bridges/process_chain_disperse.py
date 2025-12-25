# src/utils/bridges/process_chain_disperse.py
import random
import asyncio
from loguru import logger

from src.utils.planner import ActivityPlanner
from src.utils.data.bridges import BRIDGES
from src.utils.data.chains import chain_mapping
from src.modules.bridges.bridge_factory import AcrossBridge, RelayBridge, SuperBridge
from src.models.bridge import BridgeConfig
from src.models.token import Token

async def process_chain_disperse(route):
    planner = ActivityPlanner()

    current_chain = route.current_chain or 'BASE'

    # Сколько бриджей сделать сегодня (2–4)
    num_bridges = random.randint(2, 4)
    logger.info(f"BRIDGE DAY: planning {num_bridges} bridges")

    bridge_classes = [AcrossBridge, RelayBridge, SuperBridge]  # список доступных бриджей

    for i in range(num_bridges):
        # Выбираем случайную цель (или фиксированную, если нужно)
        target_chain = planner.choose_bridge_target(current_chain)
        if not target_chain:
            logger.warning("No target chain available, skipping bridge")
            continue

        # Выбираем случайный бридж-класс
        bridge_class = random.choice(bridge_classes)
        bridge_name = bridge_class.__name__.replace('Bridge', '')  # 'Across', 'Relay', 'Super'

        logger.info(f"Bridge #{i+1}/{num_bridges}: {bridge_name} | {current_chain} → {target_chain}")

        # Создаём конфиг для бриджинга
        bridge_config = BridgeConfig(
            from_chain=chain_mapping[current_chain],
            to_chain=chain_mapping[target_chain],
            from_token=Token(chain_name=current_chain, name='ETH'),
            to_token=Token(chain_name=target_chain, name='ETH'),
            amount=random.uniform(0.0005, 0.002),  # маленькие суммы для нескольких бриджей
            use_percentage=False,
            bridge_percentage=0.0
        )

        # Создаём и запускаем бридж
        bridge = bridge_class(
            private_key=route.wallet.private_key,
            bridge_config=bridge_config,
            proxy=route.wallet.proxy
        )

        success = await bridge.bridge()
        if success:
            logger.success(f"Bridge #{i+1} successful: {bridge_name}")
            # Обновляем текущую цепочку (если бридж прошёл)
            current_chain = target_chain
            route.current_chain = current_chain
        else:
            logger.error(f"Bridge #{i+1} failed: {bridge_name}")
            # Можно добавить retry или пропустить

        # Пауза между бриджами (чтобы не выглядеть как бот)
        pause = random.randint(30, 3000)
        logger.info(f"Pause between bridges: {pause} seconds")
        await asyncio.sleep(pause)

    return True  # Успех, если хотя бы один бридж прошёл (или все)
