from src.modules.uniswap import process_uniswap

CHAIN_MODULES = {
    'BASE': [
        'UNISWAP',
        'MATCHA_SWAP',
        'BUNGEE_SWAP',
        'OWLTO_SWAP',
        'RUBYSCORE_VOTE',
        'WRAPPER_UNWRAPPER',
        'CONTRACT_DEPLOY'
    ],
    'ARBITRUM': [
        'UNISWAP',
        'MATCHA_SWAP',
        'BUNGEE_SWAP'
    ],
    'OPTIMISM': [
        'UNISWAP',
        'MATCHA_SWAP'
    ],
    'LINEA': [
        'UNISWAP',
        'MATCHA_SWAP'
    ],
    'ETHEREUM': [
        'UNISWAP'
    ]
}
