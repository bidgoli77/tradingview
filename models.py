from pydantic import BaseModel
from typing import Optional, Union


class TradingViewSignal(BaseModel):
    symbol: str
    price: Union[str, float]
    time: Optional[str] = None
    signal: str
    timeframe: Optional[str] = None
    exchange: Optional[str] = None
    volume: Optional[Union[str, float]] = None


class SignalResponse(BaseModel):
    status: str
    message: str
    signal: dict | None = None