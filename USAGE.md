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

## 결과 확인

### 데이터 저장 위치

- **원본 데이터**: `data/raw/` - JSON 형식으로 저장
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

