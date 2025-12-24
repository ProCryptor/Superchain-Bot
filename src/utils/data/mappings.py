from src.utils.legacy.runner import *

module_handlers = {
    'OKX_WITHDRAW': process_cex_withdraw,

    'UNISWAP': process_uniswap,
    'MATCHA_SWAP': process_matcha_swap,
    'BUNGEE_SWAP': process_bungee_swap,
    'RELAY_SWAP': process_relay_swap,
    'OWLTO_SWAP': process_owlto_swap,

    'RUBYSCORE_VOTE': process_rubyscore_vote,

    'WRAPPER_UNWRAPPER': process_wrapper_unwrapper,

    'CONTRACT_DEPLOY': process_deploy,
    
    'RANDOM_SWAPS': process_random_swaps,
    'SWAP_ALL_TO_ETH': process_swap_all_to_eth,
    'RANDOM_TXS': process_base_activities,
}
