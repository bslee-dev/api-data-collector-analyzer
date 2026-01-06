"""
웹 대시보드 애플리케이션
FastAPI를 사용하여 데이터 시각화 대시보드를 제공합니다.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pathlib import Path
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatabaseManager
import config


def create_app():
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(title="API Data Collector & Analyzer Dashboard")
    
    # 정적 파일 및 템플릿 설정
    dashboard_dir = Path(__file__).parent
    templates_dir = dashboard_dir / "templates"
    static_dir = dashboard_dir / "static"
    
    templates_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # 데이터베이스 관리자 초기화
    db_manager = DatabaseManager()
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """대시보드 메인 페이지"""
        return templates.TemplateResponse("dashboard.html", {"request": request})
    
    @app.get("/api/stats")
    async def get_stats():
        """전체 통계 정보 조회"""
        try:
            stats = db_manager.get_statistics()
            return JSONResponse(content=stats)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/sources/{source}/sessions")
    async def get_sessions(source: str, limit: int = 10):
        """특정 소스의 최근 세션 목록 조회"""
        try:
            sessions = db_manager.get_recent_sessions(source, limit=limit)
            return JSONResponse(content=sessions)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/sources/{source}/trend")
    async def get_trend(source: str, days: int = 7):
        """트렌드 데이터 조회"""
        try:
            trend = db_manager.get_trend_data(source, days=days)
            return JSONResponse(content=trend)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/sources/{source}/session/{session_id}")
    async def get_session_data(source: str, session_id: int):
        """특정 세션의 데이터 조회"""
        try:
            data = db_manager.get_session_data(session_id, source)
            return JSONResponse(content=data)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/sources/{source}/compare")
    async def compare_sessions(source: str, session_id1: int, session_id2: int):
        """두 세션 비교"""
        try:
            comparison = db_manager.compare_sessions(source, session_id1, session_id2)
            return JSONResponse(content=comparison)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/charts/{source}/trend")
    async def get_trend_chart(source: str, days: int = 7):
        """트렌드 차트 데이터 생성"""
        try:
            import plotly.graph_objects as go
            import pandas as pd
            
            trend_data = db_manager.get_trend_data(source, days=days)
            if not trend_data:
                return JSONResponse(content={"error": "데이터가 없습니다."}, status_code=404)
            
            df = pd.DataFrame(trend_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # 소스별 차트 생성
            if source == 'reddit':
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_score', []),
                    mode='lines+markers',
                    name='평균 점수',
                    line=dict(color='#FF4500', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_comments', []),
                    mode='lines+markers',
                    name='평균 댓글 수',
                    line=dict(color='#FF6B6B', width=2),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title=f'Reddit 트렌드 ({days}일)',
                    xaxis_title='날짜',
                    yaxis_title='평균 점수',
                    yaxis2=dict(title='평균 댓글 수', overlaying='y', side='right'),
                    hovermode='x unified'
                )
            elif source == 'github':
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_stars', []),
                    mode='lines+markers',
                    name='평균 스타 수',
                    line=dict(color='#24292e', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_forks', []),
                    mode='lines+markers',
                    name='평균 포크 수',
                    line=dict(color='#28a745', width=2),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title=f'GitHub 트렌드 ({days}일)',
                    xaxis_title='날짜',
                    yaxis_title='평균 스타 수',
                    yaxis2=dict(title='평균 포크 수', overlaying='y', side='right'),
                    hovermode='x unified'
                )
            elif source == 'hackernews':
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_score', []),
                    mode='lines+markers',
                    name='평균 점수',
                    line=dict(color='#FF6600', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df.get('avg_comments', []),
                    mode='lines+markers',
                    name='평균 댓글 수',
                    line=dict(color='#FF8533', width=2),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title=f'HackerNews 트렌드 ({days}일)',
                    xaxis_title='날짜',
                    yaxis_title='평균 점수',
                    yaxis2=dict(title='평균 댓글 수', overlaying='y', side='right'),
                    hovermode='x unified'
                )
            else:
                return JSONResponse(content={"error": "지원하지 않는 소스입니다."}, status_code=400)
            
            chart_json = fig.to_json()
            return JSONResponse(content={"chart": chart_json})
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    @app.get("/api/charts/{source}/distribution")
    async def get_distribution_chart(source: str, session_id: int = None):
        """분포 차트 데이터 생성"""
        try:
            import plotly.graph_objects as go
            import pandas as pd
            
            if session_id:
                data = db_manager.get_session_data(session_id, source)
            else:
                latest_session = db_manager.get_latest_session(source)
                if not latest_session:
                    return JSONResponse(content={"error": "데이터가 없습니다."}, status_code=404)
                data = db_manager.get_session_data(latest_session['id'], source)
            
            if not data:
                return JSONResponse(content={"error": "데이터가 없습니다."}, status_code=404)
            
            df = pd.DataFrame(data)
            
            # 소스별 분포 차트
            if source == 'reddit' and 'score' in df.columns:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df['score'],
                    nbinsx=30,
                    name='점수 분포',
                    marker_color='#FF4500'
                ))
                fig.update_layout(
                    title='Reddit 점수 분포',
                    xaxis_title='점수',
                    yaxis_title='빈도'
                )
            elif source == 'github' and 'stars' in df.columns:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df['stars'],
                    nbinsx=30,
                    name='스타 분포',
                    marker_color='#24292e'
                ))
                fig.update_layout(
                    title='GitHub 스타 분포',
                    xaxis_title='스타 수',
                    yaxis_title='빈도'
                )
            elif source == 'hackernews' and 'score' in df.columns:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df['score'],
                    nbinsx=30,
                    name='점수 분포',
                    marker_color='#FF6600'
                ))
                fig.update_layout(
                    title='HackerNews 점수 분포',
                    xaxis_title='점수',
                    yaxis_title='빈도'
                )
            else:
                return JSONResponse(content={"error": "지원하지 않는 소스입니다."}, status_code=400)
            
            chart_json = fig.to_json()
            return JSONResponse(content={"chart": chart_json})
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(content={"error": str(e)}, status_code=500)
    
    return app

