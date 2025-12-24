



# ============= FIELDS =============

MOBILE_PROXY = False  # True - мобильные proxy/False - обычные proxy
ROTATE_IP = False  # Настройка только для мобильных proxy
SLIPPAGE = 0.03

# TG_BOT_TOKEN = '1234567890:abcde2VHUAfnD6vEbCeLHONvFIbdACBMJ5U'
# TG_USER_ID = 1234567890

SHUFFLE_WALLETS = True
PAUSE_BETWEEN_WALLETS = [30, 100]
PAUSE_BETWEEN_MODULES = [20, 50]
RETRIES = 3  # Сколько раз повторять 'зафейленное' действие
PAUSE_BETWEEN_RETRIES = 15  # Пауза между повторами
WAIT_FOR_RECEIPT = True     # Если True, будет ждать получения средств во входящей сети перед запуском очередного модуля


# ================ AVAILIBLE MODULES ================
# - (добавление токенов src->utils->data->tokens) - #

class RandomDailyTxConfig:
    BASE_MODULES = [
        'UNISWAP',
        'MATCHA_SWAP',
        'BUNGEE_SWAP',
        'OWLTO_SWAP',
        'RELAY_SWAP',
        'RUBYSCORE_VOTE',  # Голосование https://rubyscore.io/dashboard
        'WRAPPER_UNWRAPPER',  # Врап->Анврап ETH
        'CONTRACT_DEPLOY',  # Деплой контракта

        'SWAP_ALL_TO_ETH'  # Свапает все токены в ETH.
    ]


# ============= RANDOMISED =============

class RandomSwapsSettings:
    number_of_swaps = [2, 5]
    swap_percentage = [0.01, 0.05]


class RandomTransactionsSettings:
    transactions_by_chain = {
        'BASE': [1, 5] # берет [от; до] действий из BASE_MODULES
    }


# ============= DEXes =============

class UniswapSettings:
    from_token = ['ETH']
    to_token = ['USDC']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.05]  # 0.1 - 10%, 0.2 - 20%...
    swap_all_balance = False


class MatchaSwapSettings:
    from_token = ['ETH']
    to_token = ['USDC']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.05]
    swap_all_balance = False


class BungeeSwapSettings:
    from_token = ['ETH']
    to_token = ['USDC']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.05]
    swap_all_balance = False


class OwltoSwapSettings:
    from_token = ['ETH']
    to_token = ['USDC']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.05]
    swap_all_balance = False


class RelaySwapSettings:
    from_token = ['ETH']
    to_token = ['USDC']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.05]
    swap_all_balance = False


# ============= (UN)WRAP =============

class WrapperUnwrapperSettings:
    amount = [0.001, 0.002]
    use_all_balance = True  # Только для unwrap
    use_percentage = True  # Как wrap так и unwrap
    percentage_to_wrap = [0.1, 0.2]


# ============= OKX =============

class OKXWithdrawSettings:  # Вывод с ОКХ на кошельки
    chain = ['Base']
    token = 'ETH'
    amount = [0.001, 0.002]  # учитывайте минимальный amount 0.00204(BASE)

    min_eth_balance = 0.001  # Если в 'chain' уже есть больше min_eth_balance, то вывода не будет.


class OKXSettings:
    API_KEY = ''
    API_SECRET = ''
    API_PASSWORD = ''

    PROXY = None  # 'http://login:pass@ip:port' (если нужно)
