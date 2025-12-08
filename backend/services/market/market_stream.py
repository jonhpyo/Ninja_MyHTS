import asyncio
import json
import websockets
import ssl

BINANCE_WS_URL = "wss://stream.binance.com:9443"


class MarketStream:

    def __init__(self, market_cache):
        self.market_cache = market_cache
        self.symbols = []
        self.ws = None
        self.is_running = False

    def add_symbol(self, symbol: str):
        s = symbol.lower()
        if s not in self.symbols:
            self.symbols.append(s)

    async def connect(self):

        if not self.symbols:
            print("⚠️ 등록된 심볼 없음")
            return

        # 🔥 ticker + bookTicker 동시 수신 (last 가격 포함)
        stream_list = []
        for s in self.symbols:
            stream_list.append(f"{s}@bookTicker")
            stream_list.append(f"{s}@ticker")
            stream_list.append(f"{s}@depth20@100ms")

        streams = "/".join(stream_list)
        url = f"{BINANCE_WS_URL}/stream?streams={streams}"

        print("📡 Binance Connect →", url)

        ssl_context = ssl._create_unverified_context()
        self.is_running = True

        while self.is_running:
            try:
                async with websockets.connect(
                    url,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:

                    self.ws = ws
                    print("✅ Binance WS 연결 성공!")

                    async for msg in ws:
                        self.handle_message(msg)

            except Exception as e:
                print("🚨 Binance WS 오류:", e)
                await asyncio.sleep(3)

    def handle_message(self, msg):
        try:
            data = json.loads(msg)

            if "data" not in data:
                return

            d = data["data"]

            # depth5 메시지에는 symbol이 없으므로 stream 이름에서 symbol 추출
            stream = data.get("stream", "")
            symbol = stream.split("@")[0].upper()  # ex: btcusdt@depth5 → BTCUSDT

            bids = d.get("bids", [])
            asks = d.get("asks", [])

            if not bids or not asks:
                return

            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            last = (best_bid + best_ask) / 2

            self.market_cache.update(symbol, best_bid, best_ask, last)

        except Exception as e:
            print("⚠️ WS message 처리 오류:", e)

