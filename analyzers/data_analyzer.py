"""
데이터 분석기
수집된 데이터에 대한 통계 및 트렌드 분석을 수행합니다.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
import re


class DataAnalyzer:
    """데이터 분석을 수행하는 클래스"""
    
    def __init__(self):
        self.results = {}
    
    def analyze(self, data, source=None):
        """
        데이터 분석 수행
        
        Args:
            data: 분석할 데이터 리스트
            source: 데이터 소스 (reddit, github, hackernews)
        
        Returns:
            분석 결과 딕셔너리
        """
        if not data:
            return {}
        
        # 소스 자동 감지
        if source is None:
            source = data[0].get('source', 'unknown') if data else 'unknown'
        
        print(f"📊 데이터 분석 중: {source}")
        
        df = pd.DataFrame(data)
        results = {
            'source': source,
            'total_count': len(data),
            'timestamp': datetime.now().isoformat()
        }
        
        # 소스별 분석
        if source == 'reddit':
            results.update(self._analyze_reddit(df))
        elif source == 'github':
            results.update(self._analyze_github(df))
        elif source == 'hackernews':
            results.update(self._analyze_hackernews(df))
        
        self.results = results
        return results
    
    def _analyze_reddit(self, df):
        """Reddit 데이터 분석"""
        analysis = {}
        
        # 기본 통계
        if 'score' in df.columns:
            analysis['score_stats'] = {
                'mean': float(df['score'].mean()),
                'median': float(df['score'].median()),
                'std': float(df['score'].std()),
                'max': int(df['score'].max()),
                'min': int(df['score'].min())
            }
        
        if 'num_comments' in df.columns:
            analysis['comments_stats'] = {
                'mean': float(df['num_comments'].mean()),
                'median': float(df['num_comments'].median()),
                'max': int(df['num_comments'].max())
            }
        
        # 서브레딧별 통계
        if 'subreddit' in df.columns:
            subreddit_counts = df['subreddit'].value_counts().to_dict()
            analysis['subreddit_distribution'] = subreddit_counts
        
        # 키워드 분석
        if 'title' in df.columns:
            analysis['top_keywords'] = self._extract_keywords(df['title'].tolist())
        
        return analysis
    
    def _analyze_github(self, df):
        """GitHub 데이터 분석"""
        analysis = {}
        
        # 기본 통계
        if 'stars' in df.columns:
            analysis['stars_stats'] = {
                'mean': float(df['stars'].mean()),
                'median': float(df['stars'].median()),
                'std': float(df['stars'].std()),
                'max': int(df['stars'].max())
            }
        
        if 'forks' in df.columns:
            analysis['forks_stats'] = {
                'mean': float(df['forks'].mean()),
                'median': float(df['forks'].median()),
                'max': int(df['forks'].max())
            }
        
        # 언어별 통계
        if 'language' in df.columns:
            language_counts = df['language'].value_counts().to_dict()
            analysis['language_distribution'] = language_counts
        
        # 라이선스 분포
        if 'license' in df.columns:
            license_counts = df['license'].value_counts().to_dict()
            analysis['license_distribution'] = license_counts
        
        # 토픽 분석
        if 'topics' in df.columns:
            all_topics = []
            for topics in df['topics'].dropna():
                if isinstance(topics, list):
                    all_topics.extend(topics)
            if all_topics:
                topic_counts = Counter(all_topics)
                analysis['top_topics'] = dict(topic_counts.most_common(20))
        
        return analysis
    
    def _analyze_hackernews(self, df):
        """HackerNews 데이터 분석"""
        analysis = {}
        
        # 기본 통계
        if 'score' in df.columns:
            analysis['score_stats'] = {
                'mean': float(df['score'].mean()),
                'median': float(df['score'].median()),
                'std': float(df['score'].std()),
                'max': int(df['score'].max())
            }
        
        if 'descendants' in df.columns:
            analysis['comments_stats'] = {
                'mean': float(df['descendants'].mean()),
                'median': float(df['descendants'].median()),
                'max': int(df['descendants'].max())
            }
        
        # 키워드 분석
        if 'title' in df.columns:
            analysis['top_keywords'] = self._extract_keywords(df['title'].tolist())
        
        return analysis
    
    def _extract_keywords(self, texts, top_n=20):
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (2글자 이상 단어)
        all_words = []
        for text in texts:
            if text:
                # 소문자 변환 및 단어 추출
                words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
                all_words.extend(words)
        
        # 불용어 제거 (간단한 버전)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'this', 'that', 'these', 'those', 'from', 'as', 'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        filtered_words = [w for w in all_words if w not in stopwords and len(w) > 2]
        
        word_counts = Counter(filtered_words)
        return dict(word_counts.most_common(top_n))
    
    def save_results(self, results=None, filename=None):
        """분석 결과를 JSON 파일로 저장"""
        if results is None:
            results = self.results
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source = results.get('source', 'unknown')
            filename = f"analysis_{source}_{timestamp}.json"
        
        filepath = Path('outputs') / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 분석 결과 저장: {filepath}")
        return filepath

