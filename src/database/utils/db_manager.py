from loguru import logger
from sqlalchemy import delete

from src.database.base_models.models import WalletModel, TaskModel


async def clear_database(engine):
    async with engine.begin() as conn:
        logger.warning("⚠️ Clearing database: wallets & tasks")

        await conn.execute(delete(TaskModel))
        await conn.execute(delete(WalletModel))

        logger.success("✅ Database cleared successfully")

