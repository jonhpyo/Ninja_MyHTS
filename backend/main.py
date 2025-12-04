from fastapi import FastAPI
from backend.api.orders_api import router as orders_router
from backend.api.accounts_api import router as accounts_router
from backend.api.positions_api import router as positions_router
from backend.api.executions_api import router as executions_router
from backend.api.symbols_api import router as symbols_router
from backend.api.market_api import router as market_router
from backend.api.market_ws_api import router as market_ws_router
from backend.api.auth_api import router as auth_router
from backend.services.market.market_service import market_service

app = FastAPI(title="HTS Trading Backend")


@app.on_event("startup")
def startup_event():
    print("🔥 MarketService Startup 시작")

    market_service.add_symbol("BTCUSDT")
    market_service.add_symbol("ETHUSDT")
    market_service.add_symbol("SOLUSDT")
    market_service.add_symbol("XRPUSDT")
    market_service.add_symbol("BNBUSDT")

    market_service.start()
    print("🔥 MarketService Startup 완료")


# -----------------------------
# API 등록
# -----------------------------
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(accounts_router)
app.include_router(positions_router)
app.include_router(executions_router)
app.include_router(symbols_router)
app.include_router(market_router)
app.include_router(market_ws_router)
