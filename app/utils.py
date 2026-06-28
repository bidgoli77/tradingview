import json
from datetime import datetime, timezone
from app.database import get_conn
from app.symbols import normalize_symbol, get_symbol_meta

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def make_duplicate_key(data: dict) -> str:
    symbol = normalize_symbol(data.get('symbol', ''))
    signal = str(data.get('signal', '')).upper()
    timeframe = str(data.get('timeframe', ''))
    event_time = str(data.get('time', ''))
    return f'{symbol}|{signal}|{timeframe}|{event_time}'

def save_signal(data: dict, status='received', risk=None, ai=None, score=None, decision=None) -> dict:
    symbol = normalize_symbol(data.get('symbol', ''))
    meta = get_symbol_meta(symbol)
    row = {
        'received_at': now_utc(),
        'symbol': symbol,
        'asset_type': meta.get('asset_type'),
        'market': meta.get('market'),
        'price': str(data.get('price', '')),
        'event_time': data.get('time'),
        'signal': str(data.get('signal', '')).upper(),
        'timeframe': data.get('timeframe'),
        'exchange': data.get('exchange'),
        'volume': str(data.get('volume', '')),
        'status': status,
        'duplicate_key': make_duplicate_key(data),
        'risk_json': json.dumps(risk or {}, ensure_ascii=False),
        'ai_json': json.dumps(ai or {}, ensure_ascii=False),
        'score_json': json.dumps(score or {}, ensure_ascii=False),
        'decision': decision or ''
    }
    try:
        with get_conn() as conn:
            cur = conn.execute('''
                INSERT INTO signals (
                    received_at, symbol, asset_type, market, price, event_time, signal,
                    timeframe, exchange, volume, status, duplicate_key, risk_json,
                    ai_json, score_json, decision
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(row[k] for k in [
                'received_at','symbol','asset_type','market','price','event_time','signal',
                'timeframe','exchange','volume','status','duplicate_key','risk_json',
                'ai_json','score_json','decision'
            ]))
            conn.commit()
            row['id'] = cur.lastrowid
            row['is_duplicate'] = False
    except Exception as exc:
        if 'UNIQUE constraint failed' in str(exc):
            row['id'] = None
            row['is_duplicate'] = True
            row['status'] = 'duplicate_ignored'
        else:
            raise
    return row

def get_recent_signals(limit=100):
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM signals ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_stats():
    with get_conn() as conn:
        total = conn.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
        buys = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='BUY'").fetchone()[0]
        sells = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='SELL'").fetchone()[0]
        strong = conn.execute("SELECT COUNT(*) FROM signals WHERE decision='STRONG_WATCH'").fetchone()[0]
    return {'total_signals': total, 'buy_signals': buys, 'sell_signals': sells, 'strong_watch': strong}


def get_signal_by_id(signal_id: int):
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM signals WHERE id = ?', (signal_id,)).fetchone()
    return dict(row) if row else None


def get_latest_signal(symbol: str | None = None):
    with get_conn() as conn:
        if symbol:
            row = conn.execute('SELECT * FROM signals WHERE symbol = ? ORDER BY id DESC LIMIT 1', (normalize_symbol(symbol),)).fetchone()
        else:
            row = conn.execute('SELECT * FROM signals ORDER BY id DESC LIMIT 1').fetchone()
    return dict(row) if row else None


def get_signals_by_symbol(symbol: str, limit: int = 100):
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT * FROM signals WHERE symbol = ? ORDER BY id DESC LIMIT ?',
            (normalize_symbol(symbol), limit),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_signal_by_id(signal_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute('DELETE FROM signals WHERE id = ?', (signal_id,))
        conn.commit()
        return cur.rowcount > 0


def delete_all_signals() -> int:
    with get_conn() as conn:
        cur = conn.execute('DELETE FROM signals')
        conn.commit()
        return cur.rowcount
