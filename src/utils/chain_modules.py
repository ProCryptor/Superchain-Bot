# src/utils/chain_modules.py
import random
import asyncio
from loguru import logger

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account

from src.modules.swaps.uniswap.uniswap import Uniswap
from src.modules.swaps.swap_factory import MatchaSwap, BungeeSwap, RelaySwap  # ← правильные импорты из фабрики
from src.modules.handlers.uniswap import handle_uniswap
from src.models.chain import Chain
from src.utils.data.tokens import tokens

async def process_uniswap(route, chain_obj):
    return await handle_uniswap(route, chain_obj)
    max_attempts = 20
    attempt = 0
    success = False
    from_token = 'ETH'
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Uniswap attempt {attempt}/{max_attempts} on {chain_obj.chain_name}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_obj.rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {chain_obj.chain_name}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0005, 0.005)
            amount = base_amount
            required_eth = amount + 0.0005

            if balance_eth >= required_eth:
                logger.info(f"Enough balance for {amount:.6f} ETH swap")
                success = True
            else:
                amount = max(0.0001, float(balance_eth) - 0.0005)  # ← float для type-error
                required_eth = amount + 0.0005
                if balance_eth >= required_eth:
                    logger.warning(f"Reduced amount to {amount:.6f} ETH for swap")
                    success = True
                else:
                    from_token = random.choice(['ETH', 'USDC', 'USDT'])
                    logger.warning(f"Switching token to {from_token} for attempt {attempt}")
        except Exception as e:
            logger.error(f"Failed to check balance (attempt {attempt}): {e}")

    if not success:
        logger.warning(f"Uniswap skipped: No suitable amount/token after {max_attempts} attempts")
        return False

    try:
        uniswap = Uniswap(
            private_key=route.wallet.private_key,
            proxy=route.wallet.proxy,
            from_token=from_token,
            to_token='USDC',
            amount=amount,
            use_percentage=False,
            swap_percentage=0.0,
            swap_all_balance=False,
            chain=chain_obj
        )
        success = await uniswap.swap()
        if success:
            logger.success(f"Uniswap swap successful on {chain_obj.chain_name}")
            return True
        else:
            logger.error(f"Uniswap swap failed on {chain_obj.chain_name}")
            return False
    except Exception as e:
        logger.error(f"Uniswap error: {e}")
        return False

async def process_matcha_swap(route, chain_obj):
    max_attempts = 20
    attempt = 0
    success = False
    from_token = 'ETH'
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Matcha attempt {attempt}/{max_attempts} on {chain_obj.chain_name}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_obj.rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {chain_obj.chain_name}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0005, 0.005)
            amount = base_amount
            required_eth = amount + 0.0005

            if balance_eth >= required_eth:
                logger.info(f"Enough balance for {amount:.6f} ETH swap")
                success = True
            else:
                amount = max(0.0001, float(balance_eth) - 0.0005)
                required_eth = amount + 0.0005
                if balance_eth >= required_eth:
                    logger.warning(f"Reduced amount to {amount:.6f} ETH for swap")
                    success = True
                else:
                    from_token = random.choice(['ETH', 'USDC', 'USDT'])
                    logger.warning(f"Switching token to {from_token} for attempt {attempt}")
        except Exception as e:
            logger.error(f"Failed to check balance (attempt {attempt}): {e}")

    if not success:
        logger.warning(f"Matcha skipped: No suitable amount/token after {max_attempts} attempts")
        return False

    try:
        matcha = MatchaSwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token='USDC',
            amount=amount,
            use_percentage=False,
            swap_percentage=0.0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        success = await matcha.swap()
        if success:
            logger.success(f"Matcha swap successful on {chain_obj.chain_name}")
            return True
        else:
            logger.error(f"Matcha swap failed on {chain_obj.chain_name}")
            return False
    except Exception as e:
        logger.error(f"Matcha error: {e}")
        return False

async def process_bungee_swap(route, chain_obj):
    max_attempts = 20
    attempt = 0
    success = False
    from_token = 'ETH'
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Bungee attempt {attempt}/{max_attempts} on {chain_obj.chain_name}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_obj.rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {chain_obj.chain_name}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0005, 0.0015)
            amount = base_amount
            required_eth = amount + 0.00015

            if balance_eth >= required_eth:
                logger.info(f"Enough balance for {amount:.6f} ETH swap")
                success = True
            else:
                amount = max(0.0001, float(balance_eth) - 0.0005)
                required_eth = amount + 0.0005
                if balance_eth >= required_eth:
                    logger.warning(f"Reduced amount to {amount:.6f} ETH for swap")
                    success = True
                else:
                    from_token = random.choice(['ETH', 'USDC', 'USDT'])
                    logger.warning(f"Switching token to {from_token} for attempt {attempt}")
        except Exception as e:
            logger.error(f"Failed to check balance (attempt {attempt}): {e}")

    if not success:
        logger.warning(f"Bungee skipped: No suitable amount/token after {max_attempts} attempts")
        return False

    try:
        bungee = BungeeSwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token='USDC',
            amount=amount,
            use_percentage=False,
            swap_percentage=0.0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        success = await bungee.swap()
        if success:
            logger.success(f"Bungee swap successful on {chain_obj.chain_name}")
            return True
        else:
            logger.error(f"Bungee swap failed on {chain_obj.chain_name}")
            return False
    except Exception as e:
        logger.error(f"Bungee error: {e}")
        return False

async def process_relay_swap(route, chain_obj):
    max_attempts = 20
    attempt = 0
    success = False
    from_token = 'ETH'
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"RelaySwap attempt {attempt}/{max_attempts} on {chain_obj.chain_name}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_obj.rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {chain_obj.chain_name}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0005, 0.005)
            amount = base_amount
            required_eth = amount + 0.0005

            if balance_eth >= required_eth:
                logger.info(f"Enough balance for {amount:.6f} ETH swap")
                success = True
            else:
                amount = max(0.0001, float(balance_eth) - 0.0005)
                required_eth = amount + 0.0005
                if balance_eth >= required_eth:
                    logger.warning(f"Reduced amount to {amount:.6f} ETH for swap")
                    success = True
                else:
                    from_token = random.choice(['ETH', 'USDC', 'USDT'])
                    logger.warning(f"Switching token to {from_token} for attempt {attempt}")
        except Exception as e:
            logger.error(f"Failed to check balance (attempt {attempt}): {e}")

    if not success:
        logger.warning(f"RelaySwap skipped: No suitable amount/token after {max_attempts} attempts")
        return False

    try:
        relay = RelaySwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token='USDC',
            amount=amount,
            use_percentage=False,
            swap_percentage=0.0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        success = await relay.swap()
        if success:
            logger.success(f"RelaySwap swap successful on {chain_obj.chain_name}")
            return True
        else:
            logger.error(f"RelaySwap swap failed on {chain_obj.chain_name}")
            return False
    except Exception as e:
        logger.error(f"RelaySwap error: {e}")
        return False

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
    # ... твои другие задачи (bridge, vote и т.д.)
}
