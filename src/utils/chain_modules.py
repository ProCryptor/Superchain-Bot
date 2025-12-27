# src/utils/chain_modules.py
import random
import asyncio
from loguru import logger

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account

from src.modules.swaps.uniswap.uniswap import Uniswap
from src.modules.swaps.swap_factory import MatchaSwap, BungeeSwap, RelaySwap
from src.modules.handlers.uniswap import handle_uniswap
from src.models.chain import Chain
from src.utils.data.tokens import tokens

# Общая функция для fallback (переключение сети и токенов)
async def fallback_loop(
    route,
    chain_obj,
    max_attempts=20,
    base_amount_min=0.0005,
    base_amount_max=0.005,
    required_gas=0.0005,
    swap_class=None,
    task_name="Swap"
):
    attempt = 0
    success = False
    current_chain = chain_obj.chain_name
    from_token = 'ETH'
    to_token = random.choice(['USDC', 'USDT', 'DAI'])  # рандомный to_token
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"{task_name} attempt {attempt}/{max_attempts} on {current_chain}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(base_amount_min, base_amount_max)
            amount = base_amount
            required_eth = amount + required_gas

            if balance_eth >= required_eth:
                logger.info(f"Enough balance for {amount:.6f} ETH swap")
                success = True
            else:
                amount = max(0.0001, float(balance_eth) - required_gas)
                required_eth = amount + required_gas
                if balance_eth >= required_eth:
                    logger.warning(f"Reduced amount to {amount:.6f} ETH for swap")
                    success = True
                else:
                    # Меняем токены
                    from_token = random.choice(['ETH', 'USDC', 'USDT'])
                    to_token = random.choice(['USDC', 'USDT', 'DAI'])
                    logger.warning(f"Switching token to {from_token} → {to_token} for attempt {attempt}")

                    # Меняем цепочку
                    alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                    if alternatives:
                        current_chain = random.choice(alternatives)
                        logger.warning(f"Switching chain to {current_chain} for attempt {attempt}")

                    # Обновляем chain_obj
                    chain_obj = Chain(
                        chain_name=current_chain,
                        native_token=chain_mapping[current_chain].native_token,
                        rpc=chain_mapping[current_chain].rpc,
                        chain_id=chain_mapping[current_chain].chain_id,
                        scan=chain_mapping[current_chain].scan
                    )
        except Exception as e:
            logger.error(f"Failed to check balance (attempt {attempt}): {e}")

    if not success:
        logger.warning(f"{task_name} skipped: No suitable amount/token/chain after {max_attempts} attempts")
        return False

    try:
        swap_instance = swap_class(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            use_percentage=False,
            swap_percentage=0.0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        success = await swap_instance.swap()
        if success:
            logger.success(f"{task_name} swap successful on {chain_obj.chain_name}")
            return True
        else:
            logger.error(f"{task_name} swap failed on {chain_obj.chain_name}")
            return False
    except Exception as e:
        logger.error(f"{task_name} error: {e}")
        return False

async def process_uniswap(route, chain_obj):
    # Используем handle_uniswap + fallback
    try:
        return await handle_uniswap(route, chain_obj)
    except Exception as e:
        logger.warning(f"Uniswap failed, fallback to loop: {e}")
        return await fallback_loop(
            route,
            chain_obj,
            max_attempts=20,
            base_amount_min=0.0005,
            base_amount_max=0.005,
            required_gas=0.0005,
            swap_class=Uniswap,
            task_name="Uniswap"
        )

async def process_matcha_swap(route, chain_obj):
    return await fallback_loop(
        route,
        chain_obj,
        max_attempts=20,
        base_amount_min=0.0005,
        base_amount_max=0.005,
        required_gas=0.0005,
        swap_class=MatchaSwap,
        task_name="Matcha"
    )

async def process_bungee_swap(route, chain_obj):
    return await fallback_loop(
        route,
        chain_obj,
        max_attempts=20,
        base_amount_min=0.0005,
        base_amount_max=0.005,
        required_gas=0.0005,
        swap_class=BungeeSwap,
        task_name="Bungee"
    )

async def process_relay_swap(route, chain_obj):
    return await fallback_loop(
        route,
        chain_obj,
        max_attempts=20,
        base_amount_min=0.0005,
        base_amount_max=0.005,
        required_gas=0.0005,
        swap_class=RelaySwap,
        task_name="RelaySwap"
    )

# Список модулей для цепочек
CHAIN_MODULES = {
    'BASE': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'OPTIMISM': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'ARBITRUM': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'LINEA': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'ETHEREUM': ['UNISWAP', 'MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
}

# Связь задачи → функция
MODULE_HANDLERS = {
    'UNISWAP': process_uniswap,
    'MATCHA_SWAP': process_matcha_swap,
    'BUNGEE_SWAP': process_bungee_swap,
    'RELAY_SWAP': process_relay_swap,
}
