from collections.abc import Callable
from typing import Any, Dict, List, Optional, Tuple

import pyuseragents
from eth_typing import ChecksumAddress
from loguru import logger
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.types import TxParams

from src.models.swap import SwapConfig
from src.utils.data.tokens import tokens


RELAY_API_URL = "https://api.relay.link/quote"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


async def create_relay_swap_tx(
    self,
    swap_config: SwapConfig,
    contract: AsyncContract,
    amount_out: int,
    amount: int
) -> Tuple[Optional[TxParams], Optional[str]]:
    """
    Создаёт и отправляет swap-транзакцию через Relay (ETH <-> stable).
    """

    steps = await get_data(self, swap_config, amount)

    if not steps:
        logger.error("RelaySwap: empty steps from API")
        return None, None

    for step in steps:
        # approve мы пропускаем — approve делается отдельной логикой
        if step.get("id") == "approve":
            continue

        try:
            tx_data = step["items"][0]["data"]

            tx: TxParams = {
                "from": self.wallet_address,
                "to": self.web3.to_checksum_address(tx_data["to"]),
                "data": tx_data["data"],
                "value": int(tx_data.get("value", 0)),
                "chainId": await self.web3.eth.chain_id,
                "nonce": await self.web3.eth.get_transaction_count(self.wallet_address),
                "gas": int(tx_data.get("gas", 0)),
                "gasPrice": await self.web3.eth.gas_price,
            }

            tx_hash = await self.sign_transaction(tx)
            logger.info(f"RelaySwap tx sent: {tx_hash}")

            confirmed = await self.wait_until_tx_finished(tx_hash)
            if confirmed:
                logger.success(f"RelaySwap confirmed: {tx_hash}")
                return tx, tx["to"]

            logger.error(f"RelaySwap failed: {tx_hash}")
            return None, None

        except Exception as e:
            logger.exception(f"RelaySwap tx build error: {e}")
            return None, None

    logger.error("RelaySwap: no executable tx step found")
    return None, None


async def get_data(
    self,
    swap_config: SwapConfig,
    amount: int
) -> List[Dict[str, Any]]:
    """
    Получает steps для swap у Relay API
    """

    from_chain = swap_config.chain
    from_token = swap_config.from_token
    to_token = swap_config.to_token

    origin_chain_id = from_chain.chain_id
    destination_chain_id = from_chain.chain_id  # swap в рамках одной сети

    from_is_native = from_token.upper() == from_chain.native_token.upper()
    to_is_native = to_token.upper() == from_chain.native_token.upper()

    origin_currency = (
        ZERO_ADDRESS if from_is_native else tokens[from_chain.chain_name][from_token]
    )
    destination_currency = (
        ZERO_ADDRESS if to_is_native else tokens[from_chain.chain_name][to_token]
    )

    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://relay.link",
        "referer": "https://relay.link/",
        "user-agent": pyuseragents.random(),
    }

    payload = {
        "user": self.wallet_address,
        "originChainId": origin_chain_id,
        "destinationChainId": destination_chain_id,
        "originCurrency": origin_currency,
        "destinationCurrency": destination_currency,
        "recipient": self.wallet_address,
        "tradeType": "EXACT_INPUT",
        "amount": str(amount),
        "referrer": "relay.link/swap",
        "useExternalLiquidity": False,
    }

    try:
        response_json, status = await self.make_request(
            method="POST",
            url=RELAY_API_URL,
            headers=headers,
            json=payload,
        )

        logger.info(f"Relay API status: {status}")

        if not response_json or "steps" not in response_json:
            logger.error(f"Relay API bad response: {response_json}")
            return []

        if "errorCode" in response_json:
            logger.error(
                f"Relay API error: {response_json.get('message')} "
                f"(code {response_json.get('errorCode')})"
            )
            return []

        return response_json["steps"]

    except Exception as e:
        logger.exception(f"Relay API request failed: {e}")
        return []
