TSX_12 = {
    'RY', 'TD', 'SHOP', 'BNS', 'ENB', 'BAM', 'BMO', 'CP', 'CNR', 'CSU', 'CNQ', 'TRI'
}
CRYPTO_8 = {
    'BTCUSD', 'ETHUSD', 'SOLUSD', 'BNBUSD', 'XRPUSD', 'DOGEUSD', 'ADAUSD', 'AVAXUSD'
}
ALLOWED_SYMBOLS = TSX_12 | CRYPTO_8

SYMBOL_META = {symbol: {'asset_type': 'stock', 'market': 'TSX'} for symbol in TSX_12}
SYMBOL_META.update({symbol: {'asset_type': 'crypto', 'market': 'CRYPTO'} for symbol in CRYPTO_8})

def normalize_symbol(symbol: str) -> str:
    value = str(symbol or '').upper().strip()
    if ':' in value:
        value = value.split(':')[-1]
    for token in ['/', '-', '_', ' ']:
        value = value.replace(token, '')
    # Convert common USDT pairs to USD style for whitelist compatibility.
    if value.endswith('USDT'):
        value = value[:-4] + 'USD'
    return value

def is_allowed_symbol(symbol: str) -> bool:
    return normalize_symbol(symbol) in ALLOWED_SYMBOLS

def get_allowed_symbols():
    return sorted(ALLOWED_SYMBOLS)

def get_symbol_meta(symbol: str) -> dict:
    normalized = normalize_symbol(symbol)
    return SYMBOL_META.get(normalized, {'asset_type': 'unknown', 'market': 'unknown'})
