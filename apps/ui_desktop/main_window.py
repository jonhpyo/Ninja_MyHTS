import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox
)

BACKEND_URL = "http://127.0.0.1:9000"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyHTS (Python Desktop v0.1)")
        self.setGeometry(200, 200, 1000, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 간단한 헤더
        header = QLabel("MyHTS - Python Desktop HTS (1차 목표)")
        layout.addWidget(header)

        # 심볼 선택 + 매수/매도
        form = QHBoxLayout()
        layout.addLayout(form)

        self.combo_symbol = QComboBox()
        self.combo_symbol.addItems(["BTCUSDT", "ETHUSDT", "XRPUSDT"])
        form.addWidget(QLabel("Symbol:"))
        form.addWidget(self.combo_symbol)

        self.edit_qty = QLineEdit()
        self.edit_qty.setPlaceholderText("Quantity (e.g. 0.001)")
        form.addWidget(QLabel("Qty:"))
        form.addWidget(self.edit_qty)

        self.btn_buy = QPushButton("시장가 매수")
        self.btn_sell = QPushButton("시장가 매도")
        form.addWidget(self.btn_buy)
        form.addWidget(self.btn_sell)

        self.btn_buy.clicked.connect(self.on_buy_market)
        self.btn_sell.clicked.connect(self.on_sell_market)

        # 상태 표시
        self.label_status = QLabel("Backend 상태: 미확인")
        layout.addWidget(self.label_status)

        btn_check = QPushButton("Backend 상태 점검")
        btn_check.clicked.connect(self.check_backend)
        layout.addWidget(btn_check)

    def check_backend(self):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if r.ok:
                data = r.json()
                self.label_status.setText(f"Backend OK: {data}")
            else:
                self.label_status.setText("Backend 응답 오류")
        except Exception as e:
            self.label_status.setText(f"Backend 연결 실패: {e}")

    def _send_order(self, side: str):
        symbol = self.combo_symbol.currentText()
        try:
            qty = float(self.edit_qty.text())
        except ValueError:
            QMessageBox.warning(self, "Order", "수량을 숫자로 입력하세요.")
            return

        payload = {
            "user_id": 1,
            "account_id": 1,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "order_type": "MARKET",
            "price": None,
        }
        try:
            r = requests.post(f"{BACKEND_URL}/orders", json=payload, timeout=3)
            if not r.ok:
                QMessageBox.warning(self, "Order", f"주문 실패: {r.status_code}")
                return
            data = r.json()
            if data.get("ok"):
                QMessageBox.information(self, "Order", f"주문 접수: {data}")
            else:
                QMessageBox.warning(self, "Order", f"주문 거절: {data}")
        except Exception as e:
            QMessageBox.warning(self, "Order", f"서버 오류: {e}")

    def on_buy_market(self):
        self._send_order("BUY")

    def on_sell_market(self):
        self._send_order("SELL")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
