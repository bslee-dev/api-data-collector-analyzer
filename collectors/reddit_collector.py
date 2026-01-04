"""
Reddit 데이터 수집기
Reddit API를 사용하여 게시물 데이터를 수집합니다.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import config


class RedditCollector:
    """Reddit에서 데이터를 수집하는 클래스"""
    
    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DataAnalyticsEngineer/1.0 (Educational Project)'
        })
    
    def collect(self, subreddit='python', limit=100, sort='hot'):
        """
        Reddit에서 게시물 데이터 수집
        
        Args:
            subreddit: 서브레딧 이름
            limit: 수집할 게시물 수
            sort: 정렬 방식 (hot, new, top, rising)
        
        Returns:
            수집된 데이터 리스트
        """
        print(f"🔍 Reddit에서 데이터 수집 중: r/{subreddit} ({sort})")
        
        url = f"{self.base_url}/r/{subreddit}/{sort}.json"
        params = {'limit': min(limit, 100)}
        
        all_posts = []
        after = None
        
        while len(all_posts) < limit:
            if after:
                params['after'] = after
            
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post.get('data', {})
                    all_posts.append({
                        'id': post_data.get('id'),
                        'title': post_data.get('title'),
                        'author': post_data.get('author'),
                        'score': post_data.get('score', 0),
                        'upvote_ratio': post_data.get('upvote_ratio', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc'),
                        'url': post_data.get('url'),
                        'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                        'subreddit': post_data.get('subreddit'),
                        'selftext': post_data.get('selftext', '')[:500],  # 처음 500자만
                        'source': 'reddit'
                    })
                    
                    if len(all_posts) >= limit:
                        break
                
                after = data.get('data', {}).get('after')
                if not after:
                    break
                
                # API 레이트 리밋 방지
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Reddit 데이터 수집 오류: {e}")
                break
        
        print(f"✅ {len(all_posts)}개의 Reddit 게시물 수집 완료")
        return all_posts[:limit]
    
    def save(self, data, filename=None):
        """수집된 데이터를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reddit_{timestamp}.json"
        
        filepath = Path(config.RAW_DATA_DIR) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 데이터 저장: {filepath}")
        return filepath

