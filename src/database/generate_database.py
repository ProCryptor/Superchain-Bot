from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from src.database.models import WorkingWallets, WalletsTasks
from loguru import logger

async def generate_database(engine, private_keys, proxies):
    await clear_database(engine)

    proxy_index = 0
    for private_key in private_keys:
        proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)

        proxy_url = None
        change_link = ''

        if proxy:
            if MOBILE_PROXY:
                proxy_url, change_link = proxy.split('|')
            else:
                proxy_url = proxy

        db_utils = DataBaseUtils(
            manager_config=DataBaseManagerConfig(
                action='working_wallets'
            )
        )

        await db_utils.add_to_db(
            private_key=private_key,
            proxy=f'{proxy_url}|{change_link}' if MOBILE_PROXY else proxy_url,
            status='pending',
        )
        
        async def clear_database(engine) -> None:
            async with AsyncSession(engine) as session:
                async with session.begin():
                    for model in [WorkingWallets, WalletsTasks]:
                        await session.execute(delete(model))
                    await session.commit()
            logger.info("The database has been cleared")
