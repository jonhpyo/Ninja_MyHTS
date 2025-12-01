# MyHTS

1차 목표: Python 데스크탑 HTS (PyQt6 + FastAPI)
2차 목표: Web HTS 클라이언트
3차 목표: Mobile App (Flutter or React Native)

구조:
- apps/backend      : FastAPI 기반 API 서버
- apps/ui_desktop   : PyQt6 기반 HTS 클라이언트
- apps/marketdata   : (추가 예정) 시세/호가 수집 엔진
- apps/engine       : (추가 예정) 매칭엔진/시뮬레이터
- shared/schemas    : 공통 Pydantic 모델
