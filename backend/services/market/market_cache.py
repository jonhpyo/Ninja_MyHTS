# backend/services/market/market_cache.py
import threading
from typing import Dict, Optional


class MarketCache:
    """
    심볼별 현재 시세 캐시
    - bid, ask, last 저장
    - thread-safe
    """

    def __init__(self):
        self._data: Dict[str, dict] = {}
        self._lock = threading.Lock()

    # -------------------------------------------------
    # 🔥 Binance/WS 에서 가격 업데이트할 때 사용하는 함수
    # -------------------------------------------------
    def update(self, symbol: str, bid: float, ask: float, last: float):
        """
        symbol: "BTCUSDT" 등
        bid/ask/last: float
        """
        with self._lock:
            self._data[symbol.upper()] = {
                "bid": float(bid),
                "ask": float(ask),
                "last": float(last),
            }

    # -------------------------------------------------
    # 현재 가격 조회 (서비스/매칭엔진에서 사용)
    # -------------------------------------------------
    def get(self, symbol: str) -> Optional[dict]:
        with self._lock:
            return self._data.get(symbol.upper())

    # -------------------------------------------------
    # 등록된 전체 심볼 목록 (매칭엔진에서 사용)
    # -------------------------------------------------
    def get_all_symbols(self):
        with self._lock:
            return list(self._data.keys())
