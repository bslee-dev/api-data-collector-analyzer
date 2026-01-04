"""
설정 파일
API 키 및 기본 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API 설정
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# 데이터 저장 경로
DATA_DIR = 'data'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
OUTPUT_DIR = 'outputs'

# 수집 설정
DEFAULT_LIMIT = 100
REDDIT_SUBREDDIT = 'python'
GITHUB_LANGUAGE = 'python'
HACKERNEWS_LIMIT = 100

# 시각화 설정
FIGURE_SIZE = (12, 6)
DPI = 100

# 데이터베이스 설정
DB_PATH = os.path.join(DATA_DIR, 'collected_data.db')
ENABLE_DATABASE = True  # 데이터베이스 저장 활성화 여부

# 스케줄러 설정
SCHEDULER_MAX_RETRIES = 3  # 최대 재시도 횟수
SCHEDULER_RETRY_DELAY = 60  # 재시도 대기 시간 (초)
SCHEDULER_LOG_FILE = 'scheduler.log'  # 스케줄러 로그 파일

