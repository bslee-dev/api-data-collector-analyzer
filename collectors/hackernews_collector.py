"""
HackerNews 데이터 수집기
HackerNews API를 사용하여 스토리 데이터를 수집합니다.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import config


class HackerNewsCollector:
    """HackerNews에서 데이터를 수집하는 클래스"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
    
    def get_item(self, item_id):
        """특정 아이템 정보 가져오기"""
        url = f"{self.base_url}/item/{item_id}.json"
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def collect(self, limit=100, story_type='top'):
        """
        HackerNews에서 스토리 데이터 수집
        
        Args:
            limit: 수집할 스토리 수
            story_type: 스토리 타입 (top, new, best, ask, show, jobs)
        
        Returns:
            수집된 데이터 리스트
        """
        print(f"🔍 HackerNews에서 데이터 수집 중: {story_type} 스토리")
        
        # 스토리 ID 리스트 가져오기
        url = f"{self.base_url}/{story_type}stories.json"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:limit]
        except requests.exceptions.RequestException as e:
            print(f"❌ HackerNews 스토리 ID 수집 오류: {e}")
            return []
        
        all_stories = []
        
        for i, story_id in enumerate(story_ids, 1):
            item = self.get_item(story_id)
            
            if item and item.get('type') == 'story':
                all_stories.append({
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'by': item.get('by', ''),
                    'score': item.get('score', 0),
                    'descendants': item.get('descendants', 0),  # 댓글 수
                    'time': item.get('time'),
                    'url': item.get('url', ''),
                    'text': item.get('text', '')[:500] if item.get('text') else '',  # 처음 500자만
                    'source': 'hackernews'
                })
            
            # 진행 상황 출력
            if i % 10 == 0:
                print(f"   진행 중: {i}/{len(story_ids)}")
            
            # API 레이트 리밋 방지
            time.sleep(0.1)
        
        print(f"✅ {len(all_stories)}개의 HackerNews 스토리 수집 완료")
        return all_stories
    
    def save(self, data, filename=None):
        """수집된 데이터를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hackernews_{timestamp}.json"
        
        filepath = Path(config.RAW_DATA_DIR) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 데이터 저장: {filepath}")
        return filepath

