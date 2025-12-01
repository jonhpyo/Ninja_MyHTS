from backend.services.market.market_service import MarketService
import time

m = MarketService()
m.add_symbol("BTCUSDT")
m.start()

time.sleep(3)
print(m.get_price("BTCUSDT"))