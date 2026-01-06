"""
대시보드 서버 실행 스크립트
"""

import uvicorn
from dashboard.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

