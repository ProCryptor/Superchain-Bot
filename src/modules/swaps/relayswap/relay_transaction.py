# src/modules/swaps/relayswap/relay_transaction.py
import pyuseragents
from eth_typing import ChecksumAddress
from web3.contract import AsyncContract
from web3.types import TxParams
from loguru import logger

from src.models.swap import SwapConfig

async def create_relay_swap_tx(
        self,
        swap_config: SwapConfig,
        contract: AsyncContract,
        amount_out: int,
        amount: int
):
    steps = await get_relay_swap_data(
        self=self,
        swap_config=swap_config,
        amount=amount
    )

    if not steps:
        logger.error("RelaySwap: empty steps from API")
        return None, None

    for step in steps:
        if step.get('id') == 'approve':
            continue

        item = step['items'][0]['data']

        tx: TxParams = {
            'from': self.wallet_address,
            'to': self.web3.to_checksum_address(item['to']),
            'data': item['data'],
            'value': int(item.get('value', 0)),
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'chainId': await self.web3.eth.chain_id,
            'gasPrice': await self.web3.eth.gas_price,
            'gas': int(item['gas'])
        }

        tx_hash = await self.sign_transaction(tx)
        logger.info(f"RelaySwap tx sent: {tx_hash}")

        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            logger.success(f"RelaySwap confirmed: {tx_hash}")
            return tx, tx['to']

        logger.error(f"RelaySwap tx failed: {tx_hash}")
        return None, None

    logger.error("RelaySwap: no executable tx found")
    return None, None

async def get_relay_swap_data(
        self,
        swap_config: SwapConfig,
        amount: int
):
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'user-agent': pyuseragents.random(),
        'origin': 'https://relay.link',
        'referer': 'https://relay.link/'
    }

    from_token = swap_config.from_token
    to_token = swap_config.to_token

    json_data = {
        'user': self.wallet_address,
        'originChainId': self.chain.chain_id,
        'destinationChainId': self.chain.chain_id,
        'originCurrency':
            '0x0000000000000000000000000000000000000000'
            if from_token == chain.native_token
            else tokens[chain.chain_name][from_token]['address'],
        'destinationCurrency':
            '0x0000000000000000000000000000000000000000'
            if to_token == chain.native_token
            else tokens[chain.chain_name][to_token]['address'],
        'recipient': self.wallet_address,
        'tradeType': 'EXACT_INPUT',
        'amount': str(int(amount)),
        'referrer': 'relay.link/swap',
        'useExternalLiquidity': False,
    }

    try:
        response, status = await self.make_request(
            method='POST',
            url='https://api.relay.link/quote',
            headers=headers,
            json=json_data
        )
    except Exception as e:
        logger.error(f"RelaySwap API request failed: {e}")
        return []

    logger.info(f"RelaySwap API status: {status}")

    if not response or 'steps' not in response:
        logger.error(f"RelaySwap API error: {response}")
        return []

    return response['steps']
