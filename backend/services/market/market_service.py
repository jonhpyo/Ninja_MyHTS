import asyncio
import threading

from .market_cache import MarketCache
from .market_stream import MarketStream


class MarketService:

    def __init__(self):
        self.cache = MarketCache()
        self.stream = MarketStream(self.cache)
        self.loop = None
        self.thread = None

        self._symbols = []

    def add_symbol(self, symbol: str):
        if symbol not in self._symbols:
            self._symbols.append(symbol)

        self.stream.add_symbol(symbol)

    @property
    def symbols(self):
        """MatchingEngine 이 접근할 심볼 리스트"""
        return self._symbols

    def start(self):
        """
        FastAPI startup 이벤트에서 호출되는 함수
        Binance WS를 별도 스레드에서 실행
        """
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.stream.connect())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        print("🚀 MarketDataService 시작됨.")

    def get_price(self, symbol: str):
        return self.cache.get(symbol)

market_service = MarketService()