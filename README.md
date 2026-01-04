# 🔍 API Data Collector & Analyzer

여러 API 소스에서 데이터를 수집하고 분석하는 Data Analytics Engineer용 토이 프로젝트입니다.

## ✨ 주요 기능

- **다중 소스 데이터 수집**: Reddit, GitHub, HackerNews 등 여러 API에서 데이터 수집
- **데이터베이스 저장**: SQLite를 사용한 영구 데이터 저장 및 버전 관리
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
├── data/                   # 수집된 데이터 저장
│   ├── raw/               # 원본 데이터 (JSON)
│   ├── processed/         # 처리된 데이터
│   └── collected_data.db  # SQLite 데이터베이스
├── outputs/                # 분석 결과 및 시각화
├── config.py              # 설정 파일
└── requirements.txt       # 의존성 패키지
```

## 🎯 사용 예시

```python
from collectors.reddit_collector import RedditCollector
from analyzers.data_analyzer import DataAnalyzer

# Reddit 데이터 수집
collector = RedditCollector()
data = collector.collect(subreddit='python', limit=100)

# 데이터 분석
analyzer = DataAnalyzer()
results = analyzer.analyze(data)
analyzer.visualize(results)
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

## 🔧 설정

`.env` 파일을 생성하여 API 키를 설정할 수 있습니다 (선택사항):

```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
GITHUB_TOKEN=your_github_token
```

## 📝 라이선스

MIT License

## 🤝 기여

이슈 및 풀 리퀘스트를 환영합니다!

