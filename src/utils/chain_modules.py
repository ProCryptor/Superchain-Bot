from src.modules.swaps.uniswap.uniswap import Uniswap
from src.modules.swaps.matcha.matcha_transaction import Matcha
# дальше по аналогии

async def process_uniswap(route, chain):
    u = Uniswap(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy,
        from_token='ETH',
        to_token='USDC',
        amount=0.1,
        use_percentage=True,
        swap_percentage=0.05,
        swap_all_balance=False,
        chain=chain
    )
    return await u.swap()

async def process_matcha(route, chain):
    m = Matcha(...)
    return await m.swap()


CHAIN_MODULES = {
    'BASE': [
        'UNISWAP',
        'MATCHA_SWAP',
    ],
}

MODULE_HANDLERS = {
    'UNISWAP': process_uniswap,
    'MATCHA_SWAP': process_matcha,
}
