import random
from loguru import logger
from src.utils.planner import ActivityPlanner
from src.utils.data.bridges import BRIDGES
from src.modules.bridges.bridge_factory import ABCBridge
async def process_chain_disperse(route):
    planner = ActivityPlanner()

    current_chain = route.current_chain or 'BASE'
    target_chain = planner.choose_bridge_target(current_chain)

    if not target_chain:
        logger.info('Bridge: no available target chain')
        return False

    logger.success(f'Bridge: {current_chain} → {target_chain}')

    # ❗ Тут позже будет реальный bridge модуль
    # Сейчас — заглушка поведения
    bridge = RelayBridge(...)
    await bridge.bridge()

    route.current_chain = target_chain
    return True


async def fake_bridge_delay():
    delay = random.randint(60, 180)
    logger.info(f'Bridge tx pending... {delay}s')
    import asyncio
    await asyncio.sleep(delay)
