# 사용 가이드

## 빠른 시작

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 기본 실행

모든 소스에서 데이터를 수집하고 분석합니다:

```bash
python main.py
```

### 3. 특정 소스만 수집

```bash
# Reddit만
python main.py --source reddit

# GitHub만
python main.py --source github

# HackerNews만
python main.py --source hackernews
```

### 4. 수집 개수 조정

```bash
python main.py --source reddit --limit 50
```

### 5. 시각화 생략

```bash
python main.py --no-visualize
```

### 6. 이전 데이터와 비교 분석

```bash
python main.py --source reddit --compare
```

### 7. 데이터베이스 통계 조회

```bash
python main.py --db-stats
```

### 8. 스케줄러 모드 (자동 수집)

```bash
# 매일 자정에 자동으로 수집 (기본값)
python main.py --schedule

# 매일 특정 시간에 실행
python main.py --schedule-daily 09:00

# 6시간마다 실행
python main.py --schedule-interval 6

# 특정 소스만 스케줄링
python main.py --schedule --source reddit

# 재시도 횟수 설정
python main.py --schedule --max-retries 5
```

## 결과 확인

### 데이터 저장 위치

- **원본 데이터**: `data/raw/` - JSON 형식으로 저장
- **데이터베이스**: `data/collected_data.db` - SQLite 데이터베이스 (영구 저장)
- **분석 결과**: `outputs/` - JSON 형식으로 저장
- **시각화**: `outputs/` - PNG 이미지로 저장

### 예시 출력 파일

```
data/raw/
  ├── reddit_20260104_120000.json
  ├── github_20260104_120000.json
  └── hackernews_20260104_120000.json

outputs/
  ├── analysis_reddit_20260104_120000.json
  ├── analysis_github_20260104_120000.json
  ├── reddit_analysis_20260104_120000.png
  ├── github_analysis_20260104_120000.png
  └── hackernews_analysis_20260104_120000.png
```

## 데이터베이스 사용하기

### 데이터베이스에 저장된 데이터 조회

```python
from database import DatabaseManager

db = DatabaseManager()

# 최신 세션 정보 조회
latest = db.get_latest_session('reddit')
print(f"최신 수집 시간: {latest['collected_at']}")
print(f"수집된 항목 수: {latest['item_count']}")

# 최근 5개 세션 조회
sessions = db.get_recent_sessions('github', limit=5)
for session in sessions:
    print(f"{session['collected_at']}: {session['item_count']}개")

# 특정 세션의 데이터 조회
if sessions:
    data = db.get_session_data(sessions[0]['id'], 'github')
    print(f"첫 번째 세션 데이터: {len(data)}개")
```

### 이전 데이터와 비교

```python
from database import DatabaseManager

db = DatabaseManager()

# 최근 두 세션 비교
sessions = db.get_recent_sessions('reddit', limit=2)
if len(sessions) >= 2:
    comparison = db.compare_sessions('reddit', sessions[1]['id'], sessions[0]['id'])
    print(f"데이터 수 변화: {comparison['count_change']}개")
    print(f"평균 점수 변화: {comparison['score']['change']:.2f}")
```

### 트렌드 데이터 조회

```python
from database import DatabaseManager

db = DatabaseManager()

# 최근 7일간의 트렌드 데이터
trend = db.get_trend_data('github', days=7)
for item in trend:
    print(f"{item['date']}: 평균 스타 {item['avg_stars']:.2f}")
```

### 전체 통계 조회

```python
from database import DatabaseManager

db = DatabaseManager()

stats = db.get_statistics()
print(f"총 Reddit 게시물: {stats['total_reddit_posts']}개")
print(f"총 GitHub 저장소: {stats['total_github_repos']}개")
```

## 스케줄러 사용하기

### 스케줄러 모드 실행

스케줄러 모드는 백그라운드에서 지속적으로 실행되며, 설정한 시간에 자동으로 데이터를 수집합니다.

```bash
# 매일 자정에 모든 소스 수집
python main.py --schedule

# 매일 오전 9시에 Reddit만 수집
python main.py --schedule-daily 09:00 --source reddit

# 3시간마다 GitHub 데이터 수집
python main.py --schedule-interval 3 --source github
```

### 스케줄러 종료

스케줄러를 종료하려면 `Ctrl+C`를 누르세요. 스케줄러는 안전하게 종료되며, 현재 실행 중인 작업이 완료될 때까지 대기합니다.

### 로그 확인

스케줄러의 모든 작업은 `scheduler.log` 파일에 기록됩니다:

```bash
# 실시간 로그 확인 (Windows)
Get-Content scheduler.log -Wait

# 실시간 로그 확인 (Linux/Mac)
tail -f scheduler.log
```

### Python 코드로 스케줄러 사용

```python
from scheduler import TaskScheduler
from collectors import RedditCollector

def collect_reddit_job():
    collector = RedditCollector()
    data = collector.collect(limit=50)
    if data:
        collector.save(data)
    return data

# 스케줄러 생성
scheduler = TaskScheduler(max_retries=3)

# 매일 오전 9시에 실행
scheduler.add_daily_job(collect_reddit_job, hour=9, minute=0)

# 6시간마다 실행
scheduler.add_interval_job(collect_reddit_job, hours=6)

# 스케줄러 시작
scheduler.start()

# 백그라운드에서 실행되므로 메인 스레드는 계속 실행
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.stop()
```

## Python 코드로 사용하기

### Reddit 데이터 수집 및 분석

```python
from collectors.reddit_collector import RedditCollector
from analyzers.data_analyzer import DataAnalyzer
from analyzers.visualizer import Visualizer

# 데이터 수집
collector = RedditCollector()
data = collector.collect(subreddit='python', limit=50)

# 데이터 분석
analyzer = DataAnalyzer()
results = analyzer.analyze(data, source='reddit')

# 시각화
visualizer = Visualizer()
visualizer.visualize(data, source='reddit')
```

### GitHub 데이터 수집 및 분석

```python
from collectors.github_collector import GitHubCollector
from analyzers.data_analyzer import DataAnalyzer
from analyzers.visualizer import Visualizer

# 데이터 수집
collector = GitHubCollector()
data = collector.collect(language='python', limit=50)

# 데이터 분석
analyzer = DataAnalyzer()
results = analyzer.analyze(data, source='github')

# 시각화
visualizer = Visualizer()
visualizer.visualize(data, source='github')
```

## API 레이트 리밋

- **Reddit**: 인증 없이 사용 가능, 분당 약 60회 요청
- **GitHub**: 인증 없이 시간당 60회, 인증 시 시간당 5,000회
- **HackerNews**: 공개 API, 레이트 리밋 없음

API 레이트 리밋을 피하기 위해 코드에 자동 대기 시간이 포함되어 있습니다.

## 문제 해결

### 한글 폰트 오류

Windows에서는 기본적으로 'Malgun Gothic'을 사용합니다. 
다른 OS에서는 `analyzers/visualizer.py`의 폰트 설정을 수정하세요.

### API 연결 오류

- 인터넷 연결 확인
- 방화벽 설정 확인
- API 레이트 리밋 확인 (너무 빠르게 실행하지 마세요)

### 데이터가 수집되지 않음

- API 엔드포인트 변경 여부 확인
- 네트워크 상태 확인
- 에러 메시지 확인

