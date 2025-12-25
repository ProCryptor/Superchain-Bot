from src.modules.swaps.uniswap.uniswap import Uniswap
from config import UniswapSettings
from src.models.chain import Chain
from src.models.route import Route
from loguru import logger

async def handle_uniswap(route: Route, chain: Chain):
    uniswap = Uniswap(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy,
        amount=UniswapSettings.amount,
        from_token=UniswapSettings.from_token,
        to_token=UniswapSettings.to_token,
        use_percentage=UniswapSettings.use_percentage,
        swap_percentage=UniswapSettings.swap_percentage,
        swap_all_balance=UniswapSettings.swap_all_balance,
        chain=chain
    )
    logger.debug(uniswap)
    return await uniswap.swap()

