#==============================================================================================================
# --- Base-chain settings -- #

TASKS = ["CROSS_CHAIN_VOYAGE"]

# ============= EXAMPLES =============

ROUTE = [   
    ['xxx'] # Customize your route here
]

QUICK_BURST = [
    ['UNISWAP', 'MATCHA_SWAP', 'OKX_WITHDRAW']
]

TRADER_HUSTLE = [
    ["RANDOM_SWAPS"],
    (
        ['UNISWAP', 'BUNGEE_SWAP'],
        ['RUBYSCORE_VOTE'],
        ['WRAPPER_UNWRAPPER']
    ),
    ['SWAP_ALL_TO_ETH']
]

DEV_MARATHON = [
    ["CONTRACT_DEPLOY"],
    ["RANDOM_TXS"],
    (
        ['MATCHA_SWAP', 'OWLTO_SWAP', 'RELAY_SWAP'],
        ['RUBYSCORE_VOTE'],
        ['WRAPPER_UNWRAPPER']
    ),
    ['SWAP_ALL_TO_ETH']
]

CROSS_CHAIN_VOYAGE = [
    ["RANDOM_TXS"] 
]

FULL = [
    ["RANDOM_TXS"],
    ["RANDOM_SWAPS"],
    ["SWAP_ALL_TO_ETH"],

    ["UNISWAP"],
    ['MATCHA_SWAP'],
    ['BUNGEE_SWAP'],
    ['OWLTO_SWAP'],
    ['RELAY_SWAP'],

    ["RUBYSCORE_VOTE"],
    ["WRAPPER_UNWRAPPER"],
    ["CONTRACT_DEPLOY"],
]


# Explanation:
# - TASKS: The top-level list of tasks to execute.
# - [ ]: Only one task from the list is chosen randomly.
# - ( ): All tasks inside are executed in random order.
# - Single string: Executes as is.
# - 'OKX_WITHDRAW' - use only first
# - Module-specific settings are in config.py

#==============================================================================================================
