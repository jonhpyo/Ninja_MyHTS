import asyncio
from fastapi import WebSocket
from typing import Dict, List


class BroadcastManager:
    def __init__(self):
        self.connections: Dict[int, List[WebSocket]] = {}
        self.queue = asyncio.Queue()

    async def connect(self, account_id: int, websocket: WebSocket):
        if account_id not in self.connections:
            self.connections[account_id] = []
        self.connections[account_id].append(websocket)

    def disconnect(self, account_id: int, websocket: WebSocket):
        if account_id in self.connections:
            self.connections[account_id].remove(websocket)

    async def send(self, account_id: int, message: dict):
        """비동기 큐에 메시지만 push"""
        await self.queue.put((account_id, message))

    async def worker(self):
        """큐의 메시지를 실제 websocket 으로 전송"""
        while True:
            account_id, message = await self.queue.get()

            if account_id not in self.connections:
                continue

            remove_list = []

            for ws in self.connections[account_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    remove_list.append(ws)

            # 끊긴 연결 제거
            for ws in remove_list:
                self.disconnect(account_id, ws)


broadcast_manager = BroadcastManager()
