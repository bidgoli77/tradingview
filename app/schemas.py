from typing import Optional, Union
from pydantic import BaseModel, Field

class TradingViewSignal(BaseModel):
    symbol: str
    price: Union[str, float]
    signal: str
    time: Optional[str] = None
    timeframe: Optional[str] = None
    exchange: Optional[str] = None
    volume: Optional[Union[str, float]] = None

class ApiResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None
