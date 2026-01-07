# 🔍 API Data Collector & Analyzer

여러 API 소스에서 데이터를 수집하고 분석하는 Data Analytics Engineer용 토이 프로젝트입니다.

## ✨ 주요 기능

- **다중 소스 데이터 수집**: Reddit, GitHub, HackerNews 등 여러 API에서 데이터 수집
- **데이터베이스 저장**: SQLite를 사용한 영구 데이터 저장 및 버전 관리
- **웹 대시보드**: FastAPI 기반 실시간 데이터 시각화 대시보드
- **인터랙티브 차트**: Plotly를 사용한 인터랙티브 차트 및 그래프
- **스케줄링 및 자동화**: APScheduler를 사용한 주기적 데이터 수집
- **자동 재시도**: 실패 시 자동 재시도 로직으로 안정적인 데이터 수집
- **백그라운드 실행**: 백그라운드에서 지속적으로 실행되는 스케줄러
- **자동화된 데이터 분석**: 수집된 데이터에 대한 통계 및 트렌드 분석
- **데이터 비교 분석**: 이전 수집 데이터와 현재 데이터 비교 및 변화율 계산
- **시각화**: matplotlib을 사용한 데이터 시각화
- **데이터 저장**: JSON 및 CSV 형식으로 데이터 저장
- **확장 가능한 구조**: 새로운 API 소스 쉽게 추가 가능

## 🚀 시작하기

### 설치

```bash
pip install -r requirements.txt
```

### 사용법

```bash
# 기본 실행 (모든 소스에서 데이터 수집)
python main.py

# 특정 소스만 수집
python main.py --source reddit
python main.py --source github
python main.py --source hackernews

# 분석만 실행 (이미 수집된 데이터 사용)
python main.py --analyze-only

# 이전 데이터와 비교 분석
python main.py --source reddit --compare

# 데이터베이스 통계 조회
python main.py --db-stats

# 스케줄러 모드 (매일 자정에 자동 수집)
python main.py --schedule

# 매일 특정 시간에 실행
python main.py --schedule-daily 09:00

# N시간마다 실행
python main.py --schedule-interval 6

# 웹 대시보드 실행
python main.py --dashboard
```

## 📊 지원하는 데이터 소스

1. **Reddit**: 인기 게시물, 서브레딧 분석
2. **GitHub**: 트렌딩 저장소, 언어별 통계
3. **HackerNews**: 인기 스토리, 키워드 분석

## 📁 프로젝트 구조

```
api-data-collector-analyzer/
├── main.py                 # 메인 실행 스크립트
├── collectors/             # 데이터 수집 모듈
│   ├── __init__.py
│   ├── reddit_collector.py
│   ├── github_collector.py
│   └── hackernews_collector.py
├── analyzers/              # 데이터 분석 모듈
│   ├── __init__.py
│   ├── data_analyzer.py
│   └── visualizer.py
├── database/               # 데이터베이스 관리 모듈
│   ├── __init__.py
│   └── db_manager.py
├── scheduler/               # 스케줄러 모듈
│   ├── __init__.py
│   └── task_scheduler.py
├── dashboard/               # 웹 대시보드 모듈
│   ├── __init__.py
│   ├── app.py
│   ├── run_server.py
│   └── templates/
│       └── dashboard.html
├── data/                   # 수집된 데이터 저장
│   ├── raw/               # 원본 데이터 (JSON)
│   ├── processed/         # 처리된 데이터
│   └── collected_data.db  # SQLite 데이터베이스
├── outputs/                # 분석 결과 및 시각화
├── config.py              # 설정 파일
└── requirements.txt       # 의존성 패키지
```

## 🎯 사용 예시

### 기본 데이터 수집 및 분석

```python
from collectors.reddit_collector import RedditCollector
from analyzers.data_analyzer import DataAnalyzer
from database import DatabaseManager

# Reddit 데이터 수집
collector = RedditCollector()
data = collector.collect(subreddit='python', limit=100)

# 데이터베이스에 저장
db_manager = DatabaseManager()
db_manager.save_collection(data, 'reddit')

# 데이터 분석
analyzer = DataAnalyzer()
results = analyzer.analyze(data, source='reddit')
analyzer.save_results(results)
```

### 스케줄러 사용

```python
from scheduler import TaskScheduler
from collectors import RedditCollector

def collect_data():
    collector = RedditCollector()
    data = collector.collect(limit=50)
    return data

# 스케줄러 생성 및 설정
scheduler = TaskScheduler(max_retries=3)
scheduler.add_daily_job(collect_data, hour=9, minute=0)
scheduler.start()
```

### 웹 대시보드 API 사용

```python
import requests

# 통계 조회
response = requests.get('http://localhost:8000/api/stats')
stats = response.json()

# 트렌드 데이터 조회
response = requests.get('http://localhost:8000/api/sources/reddit/trend?days=7')
trend = response.json()
```

## 📈 분석 기능

- **통계 분석**: 평균, 중앙값, 표준편차 등 기본 통계
- **트렌드 분석**: 시간별 트렌드 분석
- **키워드 분석**: 자주 언급되는 키워드 추출
- **데이터 비교**: 이전 수집 데이터와의 비교 및 변화율 계산
- **시각화**: 차트 및 그래프 생성

## 💾 데이터베이스 기능

- **영구 저장**: SQLite 데이터베이스에 모든 수집 데이터 저장
- **버전 관리**: 각 수집 작업을 세션으로 관리하여 시간별 데이터 추적
- **비교 분석**: 두 세션 간 데이터 비교 및 변화율 계산
- **통계 조회**: 데이터베이스에 저장된 전체 통계 정보 조회
- **트렌드 추적**: 최근 N일간의 데이터 트렌드 조회

## ⏰ 스케줄링 기능

- **주기적 수집**: 매일 또는 N시간마다 자동으로 데이터 수집
- **백그라운드 실행**: 백그라운드에서 지속적으로 실행
- **자동 재시도**: 실패 시 최대 3회까지 자동 재시도
- **유연한 스케줄링**: 매일 특정 시간, 주기적 간격 등 다양한 스케줄 설정
- **로깅**: 모든 작업을 로그 파일에 기록

## 🌐 웹 대시보드 기능

- **실시간 시각화**: 수집된 데이터를 실시간으로 시각화
- **인터랙티브 차트**: Plotly를 사용한 인터랙티브 차트 (줌, 팬, 호버 등)
- **트렌드 분석**: 시간별 트렌드 차트로 데이터 변화 추적
- **분포 분석**: 히스토그램으로 데이터 분포 시각화
- **다중 소스 지원**: Reddit, GitHub, HackerNews 각각의 대시보드
- **RESTful API**: JSON API를 통한 데이터 조회
- **자동 업데이트**: 30초마다 통계 자동 갱신

### 대시보드 실행

```bash
# 기본 포트(8000)로 실행
python main.py --dashboard

# 특정 포트로 실행
python main.py --dashboard --dashboard-port 8080
```

브라우저에서 `http://localhost:8000`으로 접속하여 대시보드를 확인할 수 있습니다.

### API 엔드포인트

- `GET /api/stats` - 전체 통계 정보
- `GET /api/sources/{source}/sessions?limit=N` - 세션 목록 조회
- `GET /api/sources/{source}/trend?days=N` - 트렌드 데이터 조회
- `GET /api/sources/{source}/session/{session_id}` - 특정 세션 데이터
- `GET /api/charts/{source}/trend?days=N` - 트렌드 차트 (Plotly JSON)
- `GET /api/charts/{source}/distribution` - 분포 차트 (Plotly JSON)
- `GET /api/sources/{source}/compare?session_id1=X&session_id2=Y` - 세션 비교

## 🔧 설정

### 환경 변수 설정

`.env` 파일을 생성하여 API 키를 설정할 수 있습니다 (선택사항):

```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
GITHUB_TOKEN=your_github_token
```

### 설정 파일 (config.py)

주요 설정을 `config.py`에서 변경할 수 있습니다:

- `DEFAULT_LIMIT`: 기본 수집 개수 (기본값: 100)
- `REDDIT_SUBREDDIT`: 기본 서브레딧 (기본값: 'python')
- `GITHUB_LANGUAGE`: 기본 프로그래밍 언어 (기본값: 'python')
- `ENABLE_DATABASE`: 데이터베이스 저장 활성화 여부 (기본값: True)
- `SCHEDULER_MAX_RETRIES`: 최대 재시도 횟수 (기본값: 3)

## 📦 의존성

주요 패키지:

- `requests`: HTTP 요청
- `pandas`: 데이터 분석
- `matplotlib`, `seaborn`: 데이터 시각화
- `APScheduler`: 작업 스케줄링
- `FastAPI`, `uvicorn`: 웹 대시보드
- `plotly`: 인터랙티브 차트
- `python-dotenv`: 환경 변수 관리

전체 목록은 `requirements.txt`를 참조하세요.

## 🛠️ 개발

### 프로젝트 구조 확장

새로운 데이터 소스를 추가하려면:

1. `collectors/` 디렉토리에 새로운 collector 클래스 생성
2. `collectors/__init__.py`에 추가
3. `main.py`에 수집 함수 추가
4. `database/db_manager.py`에 저장 로직 추가 (선택사항)

### 로그 파일

- `scheduler.log`: 스케줄러 작업 로그
- 데이터베이스: `data/collected_data.db`

## 📝 라이선스

MIT License

## 🤝 기여

이슈 및 풀 리퀘스트를 환영합니다!

## 📚 추가 문서

- [USAGE.md](USAGE.md) - 상세 사용 가이드

