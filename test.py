from backend.services.market.market_service import market_service
import time

market_service.add_symbol("BTCUSDT")
market_service.start()

time.sleep(3)
print(market_service.get_price("BTCUSDT"))