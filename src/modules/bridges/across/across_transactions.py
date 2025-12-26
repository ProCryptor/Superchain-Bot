# src/modules/bridges/across/across_transactions.py
from typing import Optional, Dict, Any

import pyuseragents
from eth_typing import ChecksumAddress
from web3.contract import AsyncContract

from src.models.bridge import BridgeConfig
from src.models.contracts import AcrossBridgeData
from src.utils.data.tokens import tokens
from loguru import logger

async def get_quote(
        bridge_config: BridgeConfig,
        wallet_address: ChecksumAddress,
        amount: int,
        request_func: Callable
) -> Optional[Dict[str, Any]]:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'referer': 'https://across.to/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': pyuseragents.random(),
    }

    params = {
        'inputToken': bridge_config.from_token.address,
        'outputToken': bridge_config.to_token.address,
        'originChainId': str(bridge_config.from_chain.chain_id),
        'destinationChainId': str(bridge_config.to_chain.chain_id),
        'amount': str(amount),
        'recipient': wallet_address,
        'skipAmountLimit': 'true',
    }

    logger.debug(f"Across quote params: {params}")

    try:
        response_json, status = await request_func(
            method="GET",
            url='https://across.to/api/suggested-fees',  # ← актуальный URL (без /app)
            params=params,
            headers=headers
        )

        logger.info(f"Across API status: {status}")
        logger.info(f"Across API response: {response_json}")

        if status != 200:
            logger.error(f"Across API failed: status {status}")
            return None

        return response_json

    except Exception as e:
        logger.exception(f"Across quote failed: {e}")
        return None


async def create_across_tx(
        self,
        contract: Optional[AsyncContract],
        bridge_config: BridgeConfig,
        amount: int
) -> Optional[tuple[Dict, Optional[str]]]:
    quote = await get_quote(
        bridge_config,
        self.wallet_address,
        amount,
        self.make_request
    )

    if not quote:
        logger.error("No quote from Across API")
        return None

    # Адреса Across (актуальные на 2025)
    contracts = {
        'BASE': '0x09aea4b2242abc8bb4bb78d537a67a245a7bec64',
        'OPTIMISM': '0x6f26bf09b1c792e3228e5467807a900a503c0281',
        'ARBITRUM': '0xe35e9842fceaca96570b734083f4a58e8f7c5f2a',
    }

    contract_address = contracts.get(bridge_config.from_chain.chain_name.upper())
    if not contract_address:
        logger.error(f"No Across contract for {bridge_config.from_chain.chain_name}")
        return None

    contract = self.load_contract(
        address=contract_address,
        web3=self.web3,
        abi=AcrossBridgeData.abi
    )

    try:
        tx = await contract.functions.depositV3(
            self.wallet_address,
            self.wallet_address,
            bridge_config.from_token.address,
            bridge_config.to_token.address,
            amount,
            amount - int(quote['relayFeePct'] * amount),  # relayFeeTotal
            bridge_config.to_chain.chain_id,
            '0x0000000000000000000000000000000000000000',
            int(quote['timestamp']),
            int(quote['fillDeadline']),
            0,
            b''
        ).build_transaction({
            'value': amount,
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'from': self.wallet_address,
            'gasPrice': await self.web3.eth.gas_price,
        })
        return tx, None
    except Exception as e:
        logger.error(f"Failed to build Across tx: {e}")
        return None
