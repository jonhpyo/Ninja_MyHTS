import asyncio
import json
import websockets

# 🔥 Combined Stream 정상 URL
BINANCE_WS_URL = "wss://stream.binance.com:9443"


class MarketStream:
    """
    Binance WebSocket에서 실시간 bookTicker 데이터를 수신하여
    MarketCache에 전달하는 역할
    """

    def __init__(self, market_cache):
        self.market_cache = market_cache
        self.symbol_streams = []  # 예: ["btcusdt@bookTicker"]

    def add_symbol(self, symbol: str):
        stream_name = f"{symbol.lower()}@bookTicker"
        self.symbol_streams.append(stream_name)

    async def connect(self):
        if not self.symbol_streams:
            print("⚠️ 등록된 심볼이 없습니다. MarketStream을 시작할 수 없습니다.")
            return

        # 🔥 Combined Stream 정답 URL
        stream_query = "/".join(self.symbol_streams)
        url = f"{BINANCE_WS_URL}/stream?streams={stream_query}"

        print(f"📡 Binance 연결 시작: {url}")

        async for ws in websockets.connect(url):
            try:
                async for message in ws:
                    self.handle_message(message)
            except Exception as e:
                print("⚠️ Binance WS 오류 발생:", e)
                print("⏳ 5초 후 재연결...")
                await asyncio.sleep(5)

    def handle_message(self, message: str):
        data = json.loads(message)

        if "data" not in data:
            return

        ticker = data["data"]

        symbol = ticker["s"]              # BTCUSDT
        bid = float(ticker["b"])
        ask = float(ticker["a"])
        last = (bid + ask) / 2            # LAST 추정값

        # 캐시에 전달
        self.market_cache.update(symbol, bid, ask, last)
