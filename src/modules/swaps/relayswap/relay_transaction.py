from collections.abc import Callable

import pyuseragents
from aiohttp import ClientSession
from eth_typing import ChecksumAddress
from web3 import AsyncWeb3
from web3.contract import Contract, AsyncContract
from web3.types import TxParams

from loguru import logger
from src.models.swap import SwapConfig
from src.utils.request_client.curl_cffi_client import CurlCffiClient


async def create_relay_swap_tx(
        self,
        swap_config: SwapConfig,
        contract: AsyncContract,
        amount_out: int,
        amount: int
):
    steps = await get_data(self, swap_config, amount)
    tx = {}
    for transaction in steps:
        if transaction['id'] == 'approve':
            continue
        else:
            tx = {
                'from': self.wallet_address,
                'to': self.web3.to_checksum_address(transaction['items'][0]['data']['to']),
                'data': transaction['items'][0]['data']['data'],
                'value': int(transaction['items'][0]['data']['value']),
                'chainId': await self.web3.eth.chain_id,
                'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
                'gas': int(transaction['items'][0]['data']['gas']),
                'gasPrice': await self.web3.eth.gas_price
            }

            # Отправляем tx
            tx_hash = await self.sign_transaction(tx)
            logger.info(f"RelaySwap tx sent: {tx_hash}")
            confirmed = await self.wait_until_tx_finished(tx_hash)
            if confirmed:
                logger.success(f"RelaySwap swap confirmed: {tx_hash}")
                return tx, tx['to']
            else:
                logger.error(f"RelaySwap tx failed: {tx_hash}")
                return None, None

    logger.error("No valid transaction found in RelaySwap steps")
    return None, None
