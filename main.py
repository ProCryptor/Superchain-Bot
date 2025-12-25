from asyncio import run, set_event_loop_policy, gather, create_task, sleep
from typing import Awaitable
import random
import asyncio
import logging
import sys
import time

from loguru import logger
from termcolor import cprint
from rich.console import Console
from rich.panel import Panel
from rich import box
from config import *
from src.utils.planner import ActivityPlanner
from src.utils.data.helper import private_keys, proxies
from src.database.generate_database import generate_database
from src.database.models import init_models, engine
from src.utils.chain_modules import CHAIN_MODULES, MODULE_HANDLERS
# from src.utils.data.mappings import module_handlers
from src.utils.manage_tasks import manage_tasks
from src.utils.retrieve_route import get_routes
from src.models.route import Route
from src.models.chain import Chain
from src.utils.data.chains import chain_mapping
from src.utils.memory import MemoryManager
from src.utils.bridges.process_chain_disperse import process_chain_disperse
from src.ui.interface import get_module, LOGO_LINES, PROJECT_INFO, clear_screen, get_module_menu

# Настройка логгеров
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)
logger.add("logs/app.log", rotation="10 MB", retention="7 days")


if sys.platform == 'win32':
    set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

console = Console()

memory = MemoryManager()

async def process_task(routes: list[Route]) -> None:
    if not routes:
        logger.success('All tasks are completed')
        return

    wallet_tasks = []

    for route in routes:
        wallet_tasks.append(
            create_task(safe_process_route(route))
        )

        time_to_pause = random.randint(
            PAUSE_BETWEEN_WALLETS[0],
            PAUSE_BETWEEN_WALLETS[1]
        ) if isinstance(PAUSE_BETWEEN_WALLETS, list) else PAUSE_BETWEEN_WALLETS

        logger.info(f'Sleeping for {time_to_pause} seconds before next wallet...')
        await sleep(time_to_pause)

    await gather(*wallet_tasks, return_exceptions=True)

async def safe_process_route(route: Route):
    try:
        await process_route(route)
    except Exception as e:
        logger.error(f'Wallet {route.wallet.private_key[:6]} crashed: {e}')


async def process_route(route: Route) -> None:
    planner = ActivityPlanner()
    wallet_id = route.wallet.private_key[:10]
    planner.personality = planner.assign_wallet_personality(wallet_id)

    from src.utils.user.account import Account  # импорт (если его ещё нет в начале файла)

    account = Account(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy,
    )
    wallet_address = account.wallet_address[:6] + '...' + account.wallet_address[-4:]

    # Решаем: работает кошелёк сегодня или нет
    if not planner.should_work_today():
        logger.info(f'Wallet {route.wallet.private_key[:6]}... skips today')
        return
        
    # === CHAIN SELECTION WITH MEMORY ===
    chain_name = planner.get_chain_for_today()

    # --- MEMORY: не ходим в одну и ту же сеть подряд ---
    last_chain = memory.get_last_chain(wallet_id)
    if last_chain == chain_name:
        logger.info(
            f'Memory: avoiding same chain {chain_name}, re-rolling'
        )
        chain_name = planner.get_chain_for_today()

    route.current_chain = chain_name
    memory.remember_chain(wallet_id, chain_name)


    # Тип дня и количество tx
    day_type = planner.get_day_type()
    tx_count = planner.get_transactions_count(day_type)

    logger.info(
        f'Wallet {wallet_address} | '
        f'Chain: {chain_name} | Day: {day_type} | Planned tx: {tx_count}'
    )

    is_bridge_day = planner.is_bridge_day(day_type)

    # Прокси / IP
    if route.wallet.proxy and MOBILE_PROXY and ROTATE_IP:
        await route.wallet.proxy.change_ip()

    private_key = route.wallet.private_key

    
    if not memory.can_bridge_today(wallet_id):
        logger.info('Memory: bridge cooldown active')
        is_bridge_day = False

    if is_bridge_day:
        logger.info(f'Planner: today is BRIDGE day (logic later)')

    # Берём ТОЛЬКО нужное количество задач
    from src.utils.chain_modules import CHAIN_MODULES, MODULE_HANDLERS

    current_chain = route.current_chain
    available_tasks = [
        task for task in route.tasks
        if task in CHAIN_MODULES.get(current_chain, [])
    ]

    tasks_today = available_tasks.copy()
    random.shuffle(tasks_today)
    tasks_today = tasks_today[:tx_count]

    # === BRIDGE DAY LOGIC ===
    if is_bridge_day and 'BRIDGE_RANDOM' not in tasks_today:
        logger.info('Planner: BRIDGE day → adding BRIDGE_RANDOM as first task')
        tasks_today.insert(0, 'BRIDGE_RANDOM')

    module_tasks = []

    for task in tasks_today:
        
        if memory.was_task_recent(wallet_id, task):
            logger.info(f'Memory: skipping repeated task {task}')
            continue
        
        if task == 'BRIDGE_RANDOM':
            success = await process_chain_disperse(route)
            if success:
                memory.remember_bridge(wallet_id)
                memory.remember_task(wallet_id, task)

                # пересборка под новую сеть
                available_tasks = CHAIN_MODULES.get(current_chain, [])
                tasks_today = random.sample(
                    available_tasks,
                    min(len(available_tasks), tx_count)
                )

            break
               
        module_tasks.append(
            create_task(
                process_module(
                    task,
                    route,
                    private_key,
                    chain_name=route.current_chain
                )
            )
        )

              
        random_sleep = random.randint(
            PAUSE_BETWEEN_MODULES[0],
            PAUSE_BETWEEN_MODULES[1]
        ) if isinstance(PAUSE_BETWEEN_MODULES, list) else PAUSE_BETWEEN_MODULES

        logger.info(f'Sleeping {random_sleep} seconds before next module...')
        await sleep(random_sleep)

        # 10% шанс длинной человеческой паузы
        if random.random() < 0.1:
            long_sleep = random.randint(300, 1800)
            logger.info(f'Human pause: {long_sleep} seconds')
            await sleep(long_sleep)
                     
    await gather(*module_tasks)

    # Пауза после дня (если нужно)
    pause_days = planner.get_pause_days_after(day_type)
    if pause_days > 0:
        sleep_time = pause_days * 86400  # 24 * 60 * 60
        logger.info(f'Planner pause: {pause_days} day(s) ({sleep_time // 3600} hours)')
        await sleep(sleep_time)
    
async def process_module(task: str, route: Route, private_key: str, chain_name: str):
    retries = 3

    for attempt in range(1, retries + 1):
        try:
            chain = Chain(
                chain_name=chain_name,
                native_token=chain_mapping[chain_name].native_token,
                rpc=chain_mapping[chain_name].rpc,
                chain_id=chain_mapping[chain_name].chain_id
            )

            from src.utils.data.chain_modules import MODULE_HANDLERS

            completed = await MODULE_HANDLERS[task](route, chain)

            if completed:
                await manage_tasks(private_key, task)
            return

        except Exception as e:
            logger.error(f'{task} failed (attempt {attempt}/{retries}): {e}')
            await sleep(random.randint(10, 30))

    logger.error(f'{task} permanently failed after {retries} retries')

async def main_loop() -> None:
    clear_screen()  # очищаем экран только один раз при первом запуске
    for line in LOGO_LINES:
        console.print(line, justify="center")
    console.print(PROJECT_INFO, justify="center")

    await init_models(engine)

    while True:
        time.sleep(0.3)
        module = get_module_menu()

        if module == 3:
            logger.info("Exiting the program...")
            break

        if module == 1:
            if SHUFFLE_WALLETS:
                random.shuffle(private_keys)

            logger.debug("Generating new database")
            await generate_database(engine, private_keys, proxies)

        elif module == 2:
            logger.debug("Working with the database")
            routes = await get_routes(private_keys)
            await process_task(routes)

        else:
            logger.error("Invalid choice")


def start_event_loop(awaitable: Awaitable[None]) -> None:
    run(awaitable)

if __name__ == '__main__':
    try:
        start_event_loop(main_loop())
    except KeyboardInterrupt:
        cprint(f'\nQuick software shutdown', color='light_yellow')
        sys.exit()
