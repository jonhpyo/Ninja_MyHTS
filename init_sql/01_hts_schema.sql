-- ===============================
-- USERS
-- ===============================
CREATE TABLE users (
    user_id         SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- ACCOUNTS
-- ===============================
CREATE TABLE accounts (
    account_id          SERIAL PRIMARY KEY,
    user_id             INT REFERENCES users(user_id),
    account_type        VARCHAR(50) DEFAULT 'FUTURES',
    currency            VARCHAR(10) DEFAULT 'USD',
    balance             NUMERIC(20, 4) DEFAULT 0,
    margin_used         NUMERIC(20, 4) DEFAULT 0,
    margin_available    NUMERIC(20, 4) DEFAULT 0,
    pnl_realized        NUMERIC(20, 4) DEFAULT 0,
    pnl_unrealized      NUMERIC(20, 4) DEFAULT 0,
    status              VARCHAR(20) DEFAULT 'ACTIVE',
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- CASH TRANSACTIONS (입출금)
-- ===============================
CREATE TABLE cash_transactions (
    txn_id         SERIAL PRIMARY KEY,
    account_id     INT REFERENCES accounts(account_id),
    txn_type       VARCHAR(20),
    amount         NUMERIC(20, 4),
    created_at     TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- FUTURES CONTRACTS (상품 스펙)
-- ===============================
CREATE TABLE symbols (
    symbol_id       SERIAL PRIMARY KEY,
    symbol_code     VARCHAR(50) UNIQUE NOT NULL,
    exchange        VARCHAR(50) NOT NULL,
    tick_size       NUMERIC(20, 8) NOT NULL,
    tick_value      NUMERIC(20, 8) NOT NULL,
    multiplier      NUMERIC(20, 8) NOT NULL,
    initial_margin  NUMERIC(20, 4),
    maintenance_margin NUMERIC(20, 4),
    expiration_date TIMESTAMP NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- POSITIONS
-- ===============================
CREATE TABLE positions (
    position_id     SERIAL PRIMARY KEY,
    account_id      INT REFERENCES accounts(account_id),
    symbol_id       INT REFERENCES symbols(symbol_id),
    qty             NUMERIC(20, 4) DEFAULT 0,
    entry_price     NUMERIC(20, 8),
    realized_pnl    NUMERIC(20, 4) DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (account_id, symbol_id)
);

-- ===============================
-- ORDERS
-- ===============================
CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    account_id      INT REFERENCES accounts(account_id),
    symbol_id       INT REFERENCES symbols(symbol_id),
    side            VARCHAR(10) NOT NULL,
    qty             NUMERIC(20, 4) NOT NULL,
    order_type      VARCHAR(10) DEFAULT 'MARKET',
    request_price   NUMERIC(20, 8),
    exec_price      NUMERIC(20, 8),
    status          VARCHAR(20) DEFAULT 'FILLED',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- EXECUTIONS / FILLS
-- ===============================
CREATE TABLE executions (
    exec_id         SERIAL PRIMARY KEY,
    order_id        INT REFERENCES orders(order_id),
    account_id      INT REFERENCES accounts(account_id),
    symbol_id       INT REFERENCES symbols(symbol_id),
    side            VARCHAR(10),
    price           NUMERIC(20, 8),
    qty             NUMERIC(20, 4),
    fee             NUMERIC(20, 4) DEFAULT 0,
    exec_type       VARCHAR(20) DEFAULT 'TRADE',
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- LIQUIDATION EVENTS
-- ===============================
CREATE TABLE liquidation_events (
    liq_id          SERIAL PRIMARY KEY,
    account_id      INT REFERENCES accounts(account_id),
    symbol_id       INT REFERENCES symbols(symbol_id),
    qty_closed      NUMERIC(20, 4),
    price           NUMERIC(20, 8),
    reason          VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- MARKET PRICE
-- ===============================
CREATE TABLE market_price (
    symbol_id       INT REFERENCES symbols(symbol_id),
    price           NUMERIC(20, 8),
    bid             NUMERIC(20, 8),
    ask             NUMERIC(20, 8),
    timestamp       TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- ACCOUNT ACTIVITY LOG
-- ===============================
CREATE TABLE account_activity_log (
    log_id          SERIAL PRIMARY KEY,
    account_id      INT REFERENCES accounts(account_id),
    event_type      VARCHAR(50),
    details         JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- NOTIFICATIONS
-- ===============================
CREATE TABLE notifications (
    notify_id       SERIAL PRIMARY KEY,
    user_id         INT REFERENCES users(user_id),
    type            VARCHAR(50),
    message         TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);
