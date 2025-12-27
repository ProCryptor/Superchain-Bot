from dataclasses import dataclass

@dataclass
class ERC20:
    abi: str = open('./assets/abi/erc20.json', 'r').read()

@dataclass
class SuperBridgeData:
    address: str = None
    abi: str = None

@dataclass
class AcrossBridgeData:
    address: str = '0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64'
    abi: str = open('./assets/abi/across.json', 'r').read()

@dataclass
class MatchaSwapData:
    address: str = None  # Matcha — API-based, контракт не нужен
    abi: list = []  # Пустой список (API, не on-chain)

@dataclass
class BungeeSwapData:
    address: str = '0x3fC91A3afd70395Cd496C647d5a6CC9C4B2b7FAD'  # Socket.tech Router (Bungee)
    abi: list = [  # Реальный ABI от Socket.tech (Bungee)
        {
            "inputs": [
                {"internalType": "address", "name": "recipient", "type": "address"},
                {"internalType": "address", "name": "inputToken", "type": "address"},
                {"internalType": "uint256", "name": "inputAmount", "type": "uint256"},
                {"internalType": "address", "name": "outputToken", "type": "address"},
                {"internalType": "uint256", "name": "minOutputAmount", "type": "uint256"},
                {"internalType": "bytes", "name": "route", "type": "bytes"}
            ],
            "name": "executeSwap",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "payable",
            "type": "function"
        },
        # Добавьте полный ABI, если нужно (это минимальный)
    ]

@dataclass
class SushiswapData:
    address: str = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'  # SushiSwap Router V2 on Polygon/Optimism/Arbitrum
    abi: list = [  # SushiSwap Router ABI (стандартный Uniswap V2 Router)
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        # ... полный Uniswap V2 Router ABI
    ]

@dataclass
class OwltoData:
    address: str = '0x...owlto_contract...'  # Адрес Owlto (если есть)
    abi: list = []  # Owlto — API-based, ABI не нужен

@dataclass
class OkuData:
    address: str = None
    abi: list = []  # Oku — API

@dataclass
class DefillamaData:
    address: str = None
    abi: list = []  # DeFiLlama — API

@dataclass
class RelayData:
    address: str = None  # Relay — API-based
    abi: list = []  # Пустой список

@dataclass
class VenusData:
    abi: str = open('./assets/abi/venus.json', 'r').read()

@dataclass
class WrapData:
    abi: str = open('./assets/abi/eth.json', 'r').read()

@dataclass
class InkySwapData:
    address: str = '0xA8C1C38FF57428e5C3a34E0899Be5Cb385476507'
    abi: str = open('./assets/abi/inky.json', 'r').read()

@dataclass
class InkGMData:
    address: str = '0x9F500d075118272B3564ac6Ef2c70a9067Fd2d3F'
    abi: str = open('./assets/abi/ink_gm.json', 'r').read()

@dataclass
class RubyScoreData:
    base_address: str = '0xe10Add2ad591A7AC3CA46788a06290De017b9fB4'
    zora_address: str = '0xDC3D8318Fbaec2de49281843f5bba22e78338146'
    abi: str = open('./assets/abi/rubyscore.json', 'r').read()

@dataclass
class DeployData:
    abi: str = open('./assets/abi/deploy.json', 'r').read()
