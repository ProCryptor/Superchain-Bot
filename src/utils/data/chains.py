# src/utils/data/chains.py
from pydantic import BaseModel

class Chain(BaseModel):
    chain_name: str
    native_token: str
    rpc: str
    chain_id: int
    scan: str  # ← добавь, если нужно (из старого кода)

# Создаём экземпляры (Pydantic автоматически валидирует)
BASE = Chain(
    chain_name='BASE',
    native_token='ETH',
    rpc='https://mainnet.base.org',
    chain_id=8453,
    scan='https://basescan.org/tx'
)

OPTIMISM = Chain(
    chain_name='OPTIMISM',
    native_token='ETH',
    rpc='https://mainnet.optimism.io',
    chain_id=10,
    scan='https://optimistic.etherscan.io/tx'
)

ARBITRUM = Chain(
    chain_name='ARBITRUM',
    native_token='ETH',
    rpc='https://arb1.arbitrum.io/rpc',
    chain_id=42161,
    scan='https://arbiscan.io/tx'
)

ETHEREUM = Chain(
    chain_name='ETHEREUM',
    native_token='ETH',
    rpc='https://rpc.ankr.com/eth',
    chain_id=1,
    scan='https://etherscan.io/tx'
)

LINEA = Chain(
    chain_name='LINEA',
    native_token='ETH',
    rpc='https://rpc.linea.build',
    chain_id=59144,
    scan='https://lineascan.build/tx'
)

chain_mapping = {
    'BASE': BASE,
    'OPTIMISM': OPTIMISM,
    'ARBITRUM': ARBITRUM,
    'ETHEREUM': ETHEREUM,
    'LINEA': LINEA,
}
