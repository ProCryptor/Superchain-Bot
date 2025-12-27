import random
from loguru import logger

from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account

from src.modules.swaps.uniswap.uniswap import Uniswap
from src.modules.swaps.swap_factory import MatchaSwap, BungeeSwap, RelaySwap
from src.modules.handlers.uniswap import handle_uniswap
from src.models.chain import Chain
from src.utils.data.chains import chain_mapping
from src.utils.data.tokens import tokens


STABLES = ['USDC', 'USDT', 'DAI']
ALL_TOKENS = ['ETH'] + STABLES


async def get_erc20_balance(w3: AsyncWeb3, wallet: str, token_address: str) -> float:
    abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function",
        },
    ]
    contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=abi)
    raw = await contract.functions.balanceOf(wallet).call()
    decimals = await contract.functions.decimals().call()
    return raw / (10 ** decimals)


def choose_swap_pair():
    """
    Случайная, но ОСМЫСЛЕННАЯ пара
    """
    from_token = random.choice(ALL_TOKENS)
    to_token = random.choice([t for t in ALL_TOKENS if t != from_token])
    return from_token, to_token


async def prepare_swap(route, chain_obj):
    w3 = AsyncWeb3(AsyncHTTPProvider(chain_mapping[chain_obj.chain_name].rpc))
    account = Account.from_key(route.wallet.private_key)
    wallet = account.address

    for _ in range(20):
        from_token, to_token = choose_swap_pair()

        # === FROM ETH ===
        if from_token == 'ETH':
            eth_balance = w3.from_wei(await w3.eth.get_balance(wallet), 'ether')
            if eth_balance < 0.0004:
                continue

            amount = round(random.uniform(0.0002, eth_balance * 0.6), 6)
            return from_token, to_token, amount, chain_obj

        # === FROM ERC20 ===
        token_address = tokens[chain_obj.chain_name][from_token]
        balance = await get_erc20_balance(w3, wallet, token_address)

        if balance <= 0:
            continue

        amount = round(random.uniform(balance * 0.2, balance * 0.7), 6)
        return from_token, to_token, amount, chain_obj

    return None, None, None, None


# =========================
# UNISWAP
# =========================
async def process_uniswap(route, chain_obj):
    try:
        return await handle_uniswap(route, chain_obj)
    except Exception:
        pass

    from_token, to_token, amount, chain_obj = await prepare_swap(route, chain_obj)
    if not from_token:
        logger.warning("Uniswap skipped: no suitable balance")
        return False

    try:
        swap = Uniswap(
            private_key=route.wallet.private_key,
            proxy=route.wallet.proxy,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            use_percentage=False,
            swap_percentage=0,
            swap_all_balance=False,
            chain=chain_obj
        )
        return await swap.swap()
    except Exception as e:
        logger.error(f"Uniswap error: {e}")
        return False


# =========================
# MATCHA
# =========================
async def process_matcha_swap(route, chain_obj):
    from_token, to_token, amount, chain_obj = await prepare_swap(route, chain_obj)
    if not from_token:
        logger.warning("Matcha skipped: no suitable balance")
        return False

    try:
        swap = MatchaSwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            use_percentage=False,
            swap_percentage=0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        return await swap.swap()
    except Exception as e:
        logger.error(f"Matcha error: {e}")
        return False


# =========================
# BUNGEE
# =========================
async def process_bungee_swap(route, chain_obj):
    from_token, to_token, amount, chain_obj = await prepare_swap(route, chain_obj)
    if not from_token:
        logger.warning("Bungee skipped: no suitable balance")
        return False

    try:
        swap = BungeeSwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            use_percentage=False,
            swap_percentage=0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        return await swap.swap()
    except Exception as e:
        logger.error(f"Bungee error: {e}")
        return False


# =========================
# RELAY
# =========================
async def process_relay_swap(route, chain_obj):
    from_token, to_token, amount, chain_obj = await prepare_swap(route, chain_obj)
    if not from_token:
        logger.warning("RelaySwap skipped: no suitable balance")
        return False

    try:
        swap = RelaySwap(
            private_key=route.wallet.private_key,
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            use_percentage=False,
            swap_percentage=0,
            swap_all_balance=False,
            proxy=route.wallet.proxy,
            chain=chain_obj
        )
        return await swap.swap()
    except Exception as e:
        logger.error(f"RelaySwap error: {e}")
        return False


# =========================
# MODULE MAP
# =========================
CHAIN_MODULES = {
    'BASE': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'OPTIMISM': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'ARBITRUM': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'LINEA': ['MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
    'ETHEREUM': ['UNISWAP', 'MATCHA_SWAP', 'BUNGEE_SWAP', 'RELAY_SWAP'],
}

MODULE_HANDLERS = {
    'UNISWAP': process_uniswap,
    'MATCHA_SWAP': process_matcha_swap,
    'BUNGEE_SWAP': process_bungee_swap,
    'RELAY_SWAP': process_relay_swap,
}
