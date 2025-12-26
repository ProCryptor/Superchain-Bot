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

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account

async def process_chain_disperse(route):
    planner = ActivityPlanner()
    current_chain = route.current_chain or 'BASE'

    # Сколько бриджей сделать сегодня (2–4)
    num_bridges = random.randint(2, 4)
    logger.info(f"BRIDGE DAY: planning {num_bridges} bridges")

    bridge_classes = [AcrossBridge, RelayBridge, SuperBridge]  # доступные мосты

    success_count = 0

    for i in range(num_bridges):
        max_attempts = 20  # максимум попыток найти подходящую цель
        attempt = 0
        success = False
        target_chain = None
        amount = None

        while attempt < max_attempts and not success:
            attempt += 1
            target_chain = planner.choose_bridge_target(current_chain)
            if not target_chain:
                logger.warning(f"Attempt {attempt}/{max_attempts}: No target chain available")
                break

            bridge_class = random.choice(bridge_classes)
            bridge_name = bridge_class.__name__.replace('Bridge', '')

            logger.info(f"Bridge #{i+1}/{num_bridges} (attempt {attempt}/{max_attempts}): {bridge_name} | {current_chain} → {target_chain}")

            # Проверка баланса
            w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
            try:
                account = Account.from_key(route.wallet.private_key)
                wallet_address = account.address
                balance_wei = await w3.eth.get_balance(wallet_address)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

                base_amount = random.uniform(0.005, 0.01)
                amount = base_amount
                required_eth = amount + 0.001

                if balance_eth >= required_eth:
                    logger.info(f"Enough balance for {amount:.6f} ETH bridge")
                    success = True  # Нашли подходящий маршрут
                else:
                    # Уменьшаем сумму
                    amount = max(0.002, balance_eth - 0.001)
                    required_eth = amount + 0.001
                    if balance_eth >= required_eth:
                        logger.warning(f"Reduced amount to {amount:.6f} ETH to fit balance")
                        success = True
                    else:
                        logger.warning(f"Still insufficient ({balance_eth:.6f} ETH) for {amount:.6f} ETH")
                        # Продолжаем поиск другой цели
            except Exception as e:
                logger.error(f"Failed to check balance (attempt {attempt}): {e}")
                # Продолжаем поиск

        if not success:
            logger.warning(f"Bridge #{i+1} skipped: No suitable target chain found after {max_attempts} attempts")
            continue

        # Создаём конфиг
        bridge_config = BridgeConfig(
            from_chain=chain_mapping[current_chain],
            to_chain=chain_mapping[target_chain],
            from_token=Token(chain_name=current_chain, name='ETH'),
            to_token=Token(chain_name=target_chain, name='ETH'),
            amount=amount,
            use_percentage=False,
            bridge_percentage=0.0
        )

        # Создаём и запускаем бридж
        bridge = bridge_class(
            private_key=route.wallet.private_key,
            bridge_config=bridge_config,
            proxy=route.wallet.proxy
        )

        try:
            success = await bridge.bridge()
            if success:
                logger.success(f"Bridge #{i+1} successful: {bridge_name} | {current_chain} → {target_chain}")
                success_count += 1
                current_chain = target_chain
                route.current_chain = current_chain
            else:
                logger.error(f"Bridge #{i+1} failed: {bridge_name}")
        except Exception as e:
            logger.error(f"Bridge #{i+1} crashed: {e}")

        # Пауза между бриджами
        pause = random.randint(30, 300)
        logger.info(f"Pause between bridges: {pause} seconds")
        await asyncio.sleep(pause)

    logger.info(f"BRIDGE DAY completed: {success_count}/{num_bridges} successful")
    return success_count > 0
