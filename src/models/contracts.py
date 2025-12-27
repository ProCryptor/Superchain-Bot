from dataclasses import dataclass, field
import json  # если нужно загружать JSON

@dataclass
class ERC20:
    abi: str = field(default_factory=lambda: open('./assets/abi/erc20.json', 'r').read())

@dataclass
class SuperBridgeData:
    address: str = None
    abi: str = None

@dataclass
class AcrossBridgeData:
    address: str = '0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64'
    abi: str = field(default_factory=lambda: open('./assets/abi/across.json', 'r').read())

@dataclass
class MatchaSwapData:
    address: str = None
    abi: list = field(default_factory=list)  # API-based, пустой список

@dataclass
class BungeeSwapData:
    address: str = None  # Bungee (Socket.tech) — API-based
    abi: list = field(default_factory=list)

@dataclass
class SushiswapData:
    address: str = None
    abi: list = field(default_factory=list)  # SushiSwap — on-chain, но ABI можно добавить

@dataclass
class OwltoData:
    address: str = None
    abi: list = field(default_factory=list)  # API-based

@dataclass
class OkuData:
    address: str = None
    abi: list = field(default_factory=list)  # API-based

@dataclass
class DefillamaData:
    address: str = None
    abi: list = field(default_factory=list)  # API-based

@dataclass
class RelayData:
    address: str = None  # Relay — API-based
    abi: list = field(default_factory=list)

@dataclass
class VenusData:
    abi: str = field(default_factory=lambda: open('./assets/abi/venus.json', 'r').read())

@dataclass
class WrapData:
    abi: str = field(default_factory=lambda: open('./assets/abi/eth.json', 'r').read())

@dataclass
class InkySwapData:
    address: str = '0xA8C1C38FF57428e5C3a34E0899Be5Cb385476507'
    abi: str = field(default_factory=lambda: open('./assets/abi/inky.json', 'r').read())

@dataclass
class InkGMData:
    address: str = '0x9F500d075118272B3564ac6Ef2c70a9067Fd2d3F'
    abi: str = field(default_factory=lambda: open('./assets/abi/ink_gm.json', 'r').read())

@dataclass
class RubyScoreData:
    base_address: str = '0xe10Add2ad591A7AC3CA46788a06290De017b9fB4'
    zora_address: str = '0xDC3D8318Fbaec2de49281843f5bba22e78338146'
    abi: str = field(default_factory=lambda: open('./assets/abi/rubyscore.json', 'r').read())

@dataclass
class DeployData:
    abi: str = field(default_factory=lambda: open('./assets/abi/deploy.json', 'r').read())
