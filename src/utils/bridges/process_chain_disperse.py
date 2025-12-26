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

    # Сколько бриджей сделать (2–4)
    num_bridges = random.randint(2, 4)
    logger.info(f"BRIDGE DAY: planning {num_bridges} bridges")

    bridge_classes = [RelayBridge]

    success_count = 0

    for i in range(num_bridges):
        target_chain = planner.choose_bridge_target(current_chain)
        if not target_chain:
            logger.warning("No target chain available, skipping bridge")
            continue

        bridge_class = random.choice(bridge_classes)
        bridge_name = bridge_class.__name__.replace('Bridge', '')

        logger.info(f"Bridge #{i+1}/{num_bridges}: {bridge_name} | {current_chain} → {target_chain}")

        try:
            bridge_config = BridgeConfig(
                from_chain=chain_mapping[current_chain],
                to_chain=chain_mapping[target_chain],
                from_token=Token(chain_name=current_chain, name='ETH'),
                to_token=Token(chain_name=target_chain, name='ETH'),
                amount=random.uniform(0.002, 0.005),  # в ETH (float)
                use_percentage=False,
                bridge_percentage=0.0
            )

            bridge = bridge_class(
                private_key=route.wallet.private_key,
                bridge_config=bridge_config,
                proxy=route.wallet.proxy
            )

            success = await bridge.bridge()
            if success:
                logger.success(f"Bridge #{i+1} successful: {bridge_name}")
                success_count += 1
                current_chain = target_chain
                route.current_chain = current_chain
            else:
                logger.error(f"Bridge #{i+1} failed: {bridge_name}")
        except Exception as e:
            logger.error(f"Bridge #{i+1} crashed: {e}")
            # Продолжаем следующий бридж

        # Пауза между бриджами
        pause = random.randint(30, 300)  # 30–300 сек
        logger.info(f"Pause between bridges: {pause} seconds")
        await asyncio.sleep(pause)

    return success_count > 0  # True, если хотя бы один бридж прошёл
