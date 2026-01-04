"""
GitHub 데이터 수집기
GitHub API를 사용하여 저장소 데이터를 수집합니다.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import config


class GitHubCollector:
    """GitHub에서 데이터를 수집하는 클래스"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DataAnalyticsEngineer/1.0'
        })
        
        if config.GITHUB_TOKEN:
            self.session.headers.update({
                'Authorization': f'token {config.GITHUB_TOKEN}'
            })
    
    def collect(self, language='python', limit=100, sort='stars'):
        """
        GitHub에서 저장소 데이터 수집
        
        Args:
            language: 프로그래밍 언어
            limit: 수집할 저장소 수
            sort: 정렬 방식 (stars, forks, updated)
        
        Returns:
            수집된 데이터 리스트
        """
        print(f"🔍 GitHub에서 데이터 수집 중: {language} 언어 ({sort} 기준)")
        
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': f'language:{language}',
            'sort': sort,
            'order': 'desc',
            'per_page': min(limit, 100)
        }
        
        all_repos = []
        page = 1
        
        while len(all_repos) < limit:
            params['page'] = page
            
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                repos = data.get('items', [])
                
                for repo in repos:
                    all_repos.append({
                        'id': repo.get('id'),
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description', ''),
                        'language': repo.get('language'),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'watchers': repo.get('watchers_count', 0),
                        'open_issues': repo.get('open_issues_count', 0),
                        'created_at': repo.get('created_at'),
                        'updated_at': repo.get('updated_at'),
                        'pushed_at': repo.get('pushed_at'),
                        'size': repo.get('size', 0),
                        'url': repo.get('html_url'),
                        'topics': repo.get('topics', []),
                        'license': repo.get('license', {}).get('name') if repo.get('license') else None,
                        'source': 'github'
                    })
                    
                    if len(all_repos) >= limit:
                        break
                
                if len(repos) < 100:
                    break
                
                page += 1
                
                # API 레이트 리밋 방지
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ GitHub 데이터 수집 오류: {e}")
                break
        
        print(f"✅ {len(all_repos)}개의 GitHub 저장소 수집 완료")
        return all_repos[:limit]
    
    def save(self, data, filename=None):
        """수집된 데이터를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"github_{timestamp}.json"
        
        filepath = Path(config.RAW_DATA_DIR) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 데이터 저장: {filepath}")
        return filepath

