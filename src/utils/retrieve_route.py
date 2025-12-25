from typing import List, Optional
from loguru import logger

from src.database.base_models.pydantic_manager import DataBaseManagerConfig
from src.database.utils.db_manager import DataBaseUtils
from src.models.route import Route, Wallet


async def get_routes(private_keys) -> Optional[List[Route]]:
    db_utils = DataBaseUtils(
        manager_config=DataBaseManagerConfig(action='working_wallets')
    )

    wallets = await db_utils.get_uncompleted_wallets()
    if not wallets:
        logger.success('Все кошельки уже отработали')
        return None

    routes = []
    for wallet in wallets:
        routes.append(
            Route(
                wallet=Wallet(
                    private_key=wallet.private_key,
                    proxy=wallet.proxy,
                ),
                tasks=[]  # больше не используется
            )
        )

    return routes

