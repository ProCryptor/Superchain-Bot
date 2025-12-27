# src/utils/bridges/process_chain_disperse.py
import random
import asyncio
from loguru import logger

from src.utils.planner import ActivityPlanner
from src.utils.data.bridges import BRIDGES, BRIDGE_ROUTES  # ← добавь BRIDGE_ROUTES
from src.utils.data.chains import chain_mapping
from src.modules.bridges.bridge_factory import AcrossBridge, RelayBridge, SuperBridge
from src.models.bridge import BridgeConfig
from src.models.token import Token
from src.models.chain import Chain  # ← добавь импорт Chain
from src.utils.chain_modules import CHAIN_MODULES, MODULE_HANDLERS

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account

async def process_chain_disperse(route):
    planner = ActivityPlanner()
    current_chain = route.current_chain or 'BASE'

    # Сколько бриджей сделать сегодня (2–4)
    num_bridges = random.randint(2,4)
    logger.info(f"BRIDGE DAY: planning {num_bridges} bridges")

    bridge_classes = [RelayBridge] * 6 + [AcrossBridge] * 4  # 70% Relay, 30% Across

    success_count = 0

    for i in range(num_bridges):
        max_attempts = 20
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

            # Внутри while-loop (перед выбором bridge_class)
            bridge_class = random.choice(bridge_classes)
            bridge_name = bridge_class.__name__.replace('Bridge', '')

            # Проверяем, поддерживает ли этот мост исходную и целевую цепочку
            if bridge_name == 'Across' and (current_chain not in BRIDGE_ROUTES['ACROSS'] or target_chain not in BRIDGE_ROUTES['ACROSS']):
                logger.warning(f"Across not supported for {current_chain} → {target_chain}, skipping")
                continue

            # Если всё ок — продолжаем
            logger.info(f"Bridge #{i+1}/{num_bridges} (attempt {attempt}/{max_attempts}): {bridge_name} | {current_chain} → {target_chain}")

            w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
            try:
                account = Account.from_key(route.wallet.private_key)
                wallet_address = account.address
                balance_wei = await w3.eth.get_balance(wallet_address)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

                base_amount = random.uniform(0.00025, 0.00251)
                amount = base_amount
                required_eth = amount + 0.00031

                if balance_eth >= required_eth:
                    logger.info(f"Enough balance for {amount:.6f} ETH bridge")
                    success = True
                else:
                    amount = max(0.0002, float(balance_eth) - 0.0001)  # ← float(balance_eth)
                    required_eth = amount + 0.001
                    if balance_eth >= required_eth:
                        logger.warning(f"Reduced amount to {amount:.6f} ETH to fit balance")
                        success = True
                    else:
                        logger.warning(f"Still insufficient ({balance_eth:.6f} ETH) for {amount:.6f} ETH")
                        alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                        if alternatives:
                            current_chain = random.choice(alternatives)
                            logger.warning(f"Switching current chain to {current_chain} for attempt {attempt}")
                            route.current_chain = current_chain
            except Exception as e:
                logger.error(f"Failed to check balance (attempt {attempt}): {e}")

        if not success:
            logger.warning(f"Bridge #{i+1} skipped: No suitable target chain found after {max_attempts} attempts")
            continue

        bridge_config = BridgeConfig(
            from_chain=chain_mapping[current_chain],
            to_chain=chain_mapping[target_chain],
            from_token=Token(chain_name=current_chain, name='ETH'),
            to_token=Token(chain_name=target_chain, name='ETH'),
            amount=amount,
            use_percentage=False,
            bridge_percentage=0.0
        )

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

        pause = random.randint(30, 300)
        logger.info(f"Pause between bridges: {pause} seconds")
        await asyncio.sleep(pause)

        logger.info(f"BRIDGE DAY completed: {success_count}/{num_bridges} successful")

        # ← СВАПЫ НАЧИНАЮТСЯ ЗДЕСЬ
        logger.info(f"Starting {random.randint(2, 4)} swaps after bridge day")

        all_chains = list(chain_mapping.keys())  # все доступные цепочки
        swap_tasks = []  # список (task, chain) для выполнения
        for _ in range(random.randint(2, 4)):
            # Выбираем случайную цепочку
            current_swap_chain = random.choice(all_chains)
            chain_obj = Chain(
                chain_name=current_swap_chain,
                native_token=chain_mapping[current_swap_chain].native_token,
                rpc=chain_mapping[current_swap_chain].rpc,
                chain_id=chain_mapping[current_swap_chain].chain_id,
                scan=chain_mapping[current_swap_chain].scan
            )

            available_swaps = list(CHAIN_MODULES.get(current_swap_chain, []))
            if not available_swaps:
                logger.warning(f"No swaps available for {current_swap_chain}, skipping")
                continue

            random.shuffle(available_swaps)  # рандомный DEX
            task = random.choice(available_swaps)  # берём один случайный DEX
            swap_tasks.append((task, chain_obj, current_swap_chain))

        for task, chain_obj, swap_chain in swap_tasks:
            max_swap_attempts = 3
            swap_attempt = 0
            while swap_attempt < max_swap_attempts:
                swap_attempt += 1
                try:
                    success = await MODULE_HANDLERS[task](route, chain_obj)
                    if success:
                        logger.success(f"Swap task {task} successful on {swap_chain}")
                        break
                    else:
                        logger.error(f"Swap task {task} failed on {swap_chain} - attempt {swap_attempt}")
                except Exception as e:
                    logger.error(f"Swap task {task} crashed on {swap_chain}: {e} - attempt {swap_attempt}")
            else:
                logger.warning(f"Swap task {task} skipped after {max_swap_attempts} attempts on {swap_chain}")

            pause = random.randint(30, 120)
            logger.info(f"Pause between swaps: {pause} seconds")
            await asyncio.sleep(pause)

        return success_count > 0
