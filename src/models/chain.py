# src/models/chain.py
from __future__ import annotations
from pydantic import BaseModel
from typing import Dict


class Chain(BaseModel):
    chain_name: str
    chain_id: int
    rpc: str
    scan: str
    native_token: str

    tokens: Dict[str, str] = {}

    def get_token_address(self, symbol: str) -> str:
        symbol = symbol.upper()
        if symbol not in self.tokens:
            raise ValueError(f"Token {symbol} not found in chain {self.chain_name}")
        return self.tokens[symbol]
