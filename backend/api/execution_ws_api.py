# backend/api/execution_ws_api.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.notifier.execution_notifier import execution_notifier

router = APIRouter()


@router.websocket("/ws/executions/{account_id}")
async def ws_executions(websocket: WebSocket, account_id: int):
    await execution_notifier.connect(websocket, account_id)
    try:
        while True:
            await websocket.receive_text()  # heartbeat (실제로 값은 사용 안함)
    except WebSocketDisconnect:
        execution_notifier.disconnect(websocket, account_id)
