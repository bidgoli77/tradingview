ALLOWED_SYMBOLS = {
    # TSX 12
    "RY", "TD", "SHOP", "BNS", "ENB", "BAM",
    "BMO", "CP", "CNR", "CSU", "CNQ", "TRI",

    # Crypto 8
    "BTCUSD", "ETHUSD", "SOLUSD", "BNBUSD",
    "XRPUSD", "DOGEUSD", "ADAUSD", "AVAXUSD",
}


def normalize_symbol(symbol: str) -> str:
    symbol = str(symbol).upper().strip()

    if ":" in symbol:
        symbol = symbol.split(":")[-1]

    symbol = symbol.replace("/", "")
    symbol = symbol.replace("-", "")

    return symbol


def is_allowed_symbol(symbol: str) -> bool:
    return normalize_symbol(symbol) in ALLOWED_SYMBOLS


def get_allowed_symbols():
    return sorted(list(ALLOWED_SYMBOLS))