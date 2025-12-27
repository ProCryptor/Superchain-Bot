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
from src.utils.data.chains import chain_mapping  # ← ИМПОРТ, который не был — это причина ошибки!

async def process_uniswap(route, chain_obj):
    # Сначала пробуем handle_uniswap
    try:
        return await handle_uniswap(route, chain_obj)
    except Exception as e:
        logger.warning(f"Uniswap failed, fallback to loop: {e}")

    max_attempts = 20
    attempt = 0
    success = False
    current_chain = chain_obj.chain_name
    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
    to_token = random.choice(['ETH', 'USDT'])
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Uniswap attempt {attempt}/{max_attempts} on {current_chain}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0002, 0.002)
            amount = base_amount
            required_eth = amount + 0.0001

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
                    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
                    to_token = random.choice(['ETH', 'USDT'])
                    logger.warning(f"Switching token to {from_token} → {to_token} for attempt {attempt}")

                    alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                    if alternatives:
                        current_chain = random.choice(alternatives)
                        logger.warning(f"Switching chain to {current_chain} for attempt {attempt}")

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
        logger.warning(f"Uniswap skipped: No suitable amount/token/chain after {max_attempts} attempts")
        return False

    try:
        uniswap = Uniswap(
            private_key=route.wallet.private_key,
            proxy=route.wallet.proxy,
            from_token=from_token,
            to_token=to_token,
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
    current_chain = chain_obj.chain_name
    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
    to_token = random.choice(['ETH', 'USDT'])
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Matcha attempt {attempt}/{max_attempts} on {current_chain}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0001, 0.002)
            amount = base_amount
            required_eth = amount + 0.0001

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
                    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
                    to_token = random.choice(['ETH', 'USDT'])
                    logger.warning(f"Switching token to {from_token} → {to_token} for attempt {attempt}")

                    alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                    if alternatives:
                        current_chain = random.choice(alternatives)
                        logger.warning(f"Switching chain to {current_chain} for attempt {attempt}")

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
        logger.warning(f"Matcha skipped: No suitable amount/token/chain after {max_attempts} attempts")
        return False

    try:
        matcha = MatchaSwap(
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
    current_chain = chain_obj.chain_name
    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
    to_token = random.choice(['ETH', 'USDT'])
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"Bungee attempt {attempt}/{max_attempts} on {current_chain}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0001, 0.002)
            amount = base_amount
            required_eth = amount + 0.0001

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
                    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
                    to_token = random.choice(['USDC', 'USDT'])
                    logger.warning(f"Switching token to {from_token} → {to_token} for attempt {attempt}")

                    alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                    if alternatives:
                        current_chain = random.choice(alternatives)
                        logger.warning(f"Switching chain to {current_chain} for attempt {attempt}")

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
        logger.warning(f"Bungee skipped: No suitable amount/token/chain after {max_attempts} attempts")
        return False

    try:
        bungee = BungeeSwap(
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
    current_chain = chain_obj.chain_name
    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
    to_token = random.choice(['ETH', 'USDT'])
    amount = None

    while attempt < max_attempts and not success:
        attempt += 1
        logger.info(f"RelaySwap attempt {attempt}/{max_attempts} on {current_chain}")

        w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[current_chain].rpc))
        try:
            account = Account.from_key(route.wallet.private_key)
            wallet_address = account.address
            balance_wei = await w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            logger.info(f"Balance in {current_chain}: {balance_eth:.6f} ETH")

            base_amount = random.uniform(0.0001, 0.002)
            amount = base_amount
            required_eth = amount + 0.0001

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
                    from_token = random.choice(['ETH', 'USDC', 'USDT', 'DAI'])
                    to_token = random.choice(['ETH', 'USDT'])
                    logger.warning(f"Switching token to {from_token} → {to_token} for attempt {attempt}")

                    alternatives = [c for c in chain_mapping.keys() if c != current_chain]
                    if alternatives:
                        current_chain = random.choice(alternatives)
                        logger.warning(f"Switching chain to {current_chain} for attempt {attempt}")

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
        logger.warning(f"RelaySwap skipped: No suitable amount/token/chain after {max_attempts} attempts")
        return False

    try:
        relay = RelaySwap(
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
}
