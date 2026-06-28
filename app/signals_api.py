from fastapi import APIRouter, HTTPException, Query
from app.utils import (
    get_recent_signals,
    get_signal_by_id,
    delete_signal_by_id,
    delete_all_signals,
    get_latest_signal,
    get_signals_by_symbol,
)
from app.symbols import normalize_symbol, is_allowed_symbol

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
def list_signals(limit: int = Query(100, ge=1, le=1000), symbol: str | None = None):
    if symbol:
        normalized = normalize_symbol(symbol)
        if not is_allowed_symbol(normalized):
            raise HTTPException(status_code=404, detail=f"Symbol not allowed: {symbol}")
        rows = get_signals_by_symbol(normalized, limit)
    else:
        rows = get_recent_signals(limit)
    return {"count": len(rows), "signals": rows}


@router.get("/latest")
def latest_signal(symbol: str | None = None):
    if symbol:
        normalized = normalize_symbol(symbol)
        if not is_allowed_symbol(normalized):
            raise HTTPException(status_code=404, detail=f"Symbol not allowed: {symbol}")
        row = get_latest_signal(normalized)
    else:
        row = get_latest_signal()
    return {"signal": row}


@router.get("/{signal_id}")
def get_signal(signal_id: int):
    row = get_signal_by_id(signal_id)
    if not row:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"signal": row}


@router.delete("/{signal_id}")
def delete_signal(signal_id: int):
    deleted = delete_signal_by_id(signal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"status": "success", "deleted_id": signal_id}


@router.delete("")
def clear_signals(confirm: str = ""):
    if confirm != "YES":
        raise HTTPException(status_code=400, detail="To delete all signals, call /signals?confirm=YES")
    deleted = delete_all_signals()
    return {"status": "success", "deleted_count": deleted}
