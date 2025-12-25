# src/models/chain.py
from __future__ import annotations
from pydantic import BaseModel


class Chain(BaseModel):
    chain_name: str
    chain_id: int
    rpc: str
    scan: str
    native_token: str

    class Config:
        arbitrary_types_allowed = True
