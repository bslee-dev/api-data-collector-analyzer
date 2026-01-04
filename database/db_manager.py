"""
데이터베이스 관리자
SQLite를 사용하여 수집된 데이터를 영구 저장하고 관리합니다.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import config


class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        데이터베이스 관리자 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로 (기본값: data/collected_data.db)
        """
        if db_path is None:
            db_path = Path(config.DATA_DIR) / 'collected_data.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        """데이터베이스 연결 생성"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return conn
    
    def _init_database(self):
        """데이터베이스 스키마 초기화"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 수집 세션 테이블 (각 수집 작업을 기록)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                collected_at TIMESTAMP NOT NULL,
                item_count INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reddit 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reddit_posts (
                id TEXT PRIMARY KEY,
                session_id INTEGER,
                title TEXT NOT NULL,
                author TEXT,
                score INTEGER DEFAULT 0,
                upvote_ratio REAL,
                num_comments INTEGER DEFAULT 0,
                created_utc REAL,
                url TEXT,
                permalink TEXT,
                subreddit TEXT,
                selftext TEXT,
                collected_at TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES collection_sessions(id)
            )
        ''')
        
        # GitHub 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_repos (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                name TEXT NOT NULL,
                full_name TEXT,
                description TEXT,
                language TEXT,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                watchers INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                pushed_at TEXT,
                size INTEGER,
                url TEXT,
                license TEXT,
                topics TEXT,
                collected_at TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES collection_sessions(id)
            )
        ''')
        
        # HackerNews 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hackernews_stories (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                title TEXT NOT NULL,
                by TEXT,
                score INTEGER DEFAULT 0,
                descendants INTEGER DEFAULT 0,
                time INTEGER,
                url TEXT,
                text TEXT,
                collected_at TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES collection_sessions(id)
            )
        ''')
        
        # 인덱스 생성 (조회 성능 향상)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sessions_source_date 
            ON collection_sessions(source, collected_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_reddit_collected_at 
            ON reddit_posts(collected_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_github_collected_at 
            ON github_repos(collected_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hackernews_collected_at 
            ON hackernews_stories(collected_at)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ 데이터베이스 초기화 완료: {self.db_path}")
    
    def save_collection(self, data: List[Dict], source: str, metadata: Optional[Dict] = None) -> int:
        """
        수집된 데이터를 데이터베이스에 저장
        
        Args:
            data: 수집된 데이터 리스트
            source: 데이터 소스 (reddit, github, hackernews)
            metadata: 추가 메타데이터
        
        Returns:
            생성된 세션 ID
        """
        if not data:
            return None
        
        conn = self._get_connection()
        cursor = conn.cursor()
        collected_at = datetime.now()
        
        # 세션 생성
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute('''
            INSERT INTO collection_sessions (source, collected_at, item_count, metadata)
            VALUES (?, ?, ?, ?)
        ''', (source, collected_at, len(data), metadata_json))
        
        session_id = cursor.lastrowid
        
        # 소스별 데이터 저장
        if source == 'reddit':
            self._save_reddit_data(cursor, data, session_id, collected_at)
        elif source == 'github':
            self._save_github_data(cursor, data, session_id, collected_at)
        elif source == 'hackernews':
            self._save_hackernews_data(cursor, data, session_id, collected_at)
        
        conn.commit()
        conn.close()
        
        print(f"💾 데이터베이스 저장 완료: {len(data)}개 항목 (세션 ID: {session_id})")
        return session_id
    
    def _save_reddit_data(self, cursor, data: List[Dict], session_id: int, collected_at: datetime):
        """Reddit 데이터 저장"""
        for item in data:
            cursor.execute('''
                INSERT OR REPLACE INTO reddit_posts 
                (id, session_id, title, author, score, upvote_ratio, num_comments,
                 created_utc, url, permalink, subreddit, selftext, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('id'),
                session_id,
                item.get('title'),
                item.get('author'),
                item.get('score', 0),
                item.get('upvote_ratio'),
                item.get('num_comments', 0),
                item.get('created_utc'),
                item.get('url'),
                item.get('permalink'),
                item.get('subreddit'),
                item.get('selftext', ''),
                collected_at
            ))
    
    def _save_github_data(self, cursor, data: List[Dict], session_id: int, collected_at: datetime):
        """GitHub 데이터 저장"""
        for item in data:
            topics_json = json.dumps(item.get('topics', [])) if item.get('topics') else None
            cursor.execute('''
                INSERT OR REPLACE INTO github_repos 
                (id, session_id, name, full_name, description, language, stars, forks,
                 watchers, open_issues, created_at, updated_at, pushed_at, size, url,
                 license, topics, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('id'),
                session_id,
                item.get('name'),
                item.get('full_name'),
                item.get('description'),
                item.get('language'),
                item.get('stars', 0),
                item.get('forks', 0),
                item.get('watchers', 0),
                item.get('open_issues', 0),
                item.get('created_at'),
                item.get('updated_at'),
                item.get('pushed_at'),
                item.get('size', 0),
                item.get('url'),
                item.get('license'),
                topics_json,
                collected_at
            ))
    
    def _save_hackernews_data(self, cursor, data: List[Dict], session_id: int, collected_at: datetime):
        """HackerNews 데이터 저장"""
        for item in data:
            cursor.execute('''
                INSERT OR REPLACE INTO hackernews_stories 
                (id, session_id, title, by, score, descendants, time, url, text, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('id'),
                session_id,
                item.get('title'),
                item.get('by'),
                item.get('score', 0),
                item.get('descendants', 0),
                item.get('time'),
                item.get('url', ''),
                item.get('text', ''),
                collected_at
            ))
    
    def get_latest_session(self, source: str) -> Optional[Dict]:
        """
        특정 소스의 최신 수집 세션 정보 조회
        
        Args:
            source: 데이터 소스
        
        Returns:
            세션 정보 딕셔너리 또는 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM collection_sessions
            WHERE source = ?
            ORDER BY collected_at DESC
            LIMIT 1
        ''', (source,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_session_data(self, session_id: int, source: str) -> List[Dict]:
        """
        특정 세션의 데이터 조회
        
        Args:
            session_id: 세션 ID
            source: 데이터 소스
        
        Returns:
            데이터 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if source == 'reddit':
            cursor.execute('''
                SELECT * FROM reddit_posts
                WHERE session_id = ?
                ORDER BY score DESC
            ''', (session_id,))
        elif source == 'github':
            cursor.execute('''
                SELECT * FROM github_repos
                WHERE session_id = ?
                ORDER BY stars DESC
            ''', (session_id,))
        elif source == 'hackernews':
            cursor.execute('''
                SELECT * FROM hackernews_stories
                WHERE session_id = ?
                ORDER BY score DESC
            ''', (session_id,))
        else:
            conn.close()
            return []
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recent_sessions(self, source: str, limit: int = 10) -> List[Dict]:
        """
        최근 수집 세션 목록 조회
        
        Args:
            source: 데이터 소스
            limit: 조회할 세션 수
        
        Returns:
            세션 정보 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM collection_sessions
            WHERE source = ?
            ORDER BY collected_at DESC
            LIMIT ?
        ''', (source, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def compare_sessions(self, source: str, session_id1: int, session_id2: int) -> Dict:
        """
        두 세션의 데이터를 비교 분석
        
        Args:
            source: 데이터 소스
            session_id1: 첫 번째 세션 ID
            session_id2: 두 번째 세션 ID
        
        Returns:
            비교 결과 딕셔너리
        """
        data1 = self.get_session_data(session_id1, source)
        data2 = self.get_session_data(session_id2, source)
        
        if not data1 or not data2:
            return {'error': '세션 데이터를 찾을 수 없습니다.'}
        
        comparison = {
            'source': source,
            'session1_id': session_id1,
            'session2_id': session_id2,
            'session1_count': len(data1),
            'session2_count': len(data2),
            'count_change': len(data2) - len(data1),
            'count_change_percent': ((len(data2) - len(data1)) / len(data1) * 100) if len(data1) > 0 else 0
        }
        
        # 소스별 비교 분석
        if source == 'reddit':
            comparison.update(self._compare_reddit(data1, data2))
        elif source == 'github':
            comparison.update(self._compare_github(data1, data2))
        elif source == 'hackernews':
            comparison.update(self._compare_hackernews(data1, data2))
        
        return comparison
    
    def _compare_reddit(self, data1: List[Dict], data2: List[Dict]) -> Dict:
        """Reddit 데이터 비교"""
        import pandas as pd
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        comparison = {}
        
        if 'score' in df1.columns and 'score' in df2.columns:
            comparison['score'] = {
                'session1_mean': float(df1['score'].mean()),
                'session2_mean': float(df2['score'].mean()),
                'change': float(df2['score'].mean() - df1['score'].mean()),
                'change_percent': float((df2['score'].mean() - df1['score'].mean()) / df1['score'].mean() * 100) if df1['score'].mean() > 0 else 0
            }
        
        if 'num_comments' in df1.columns and 'num_comments' in df2.columns:
            comparison['comments'] = {
                'session1_mean': float(df1['num_comments'].mean()),
                'session2_mean': float(df2['num_comments'].mean()),
                'change': float(df2['num_comments'].mean() - df1['num_comments'].mean()),
                'change_percent': float((df2['num_comments'].mean() - df1['num_comments'].mean()) / df1['num_comments'].mean() * 100) if df1['num_comments'].mean() > 0 else 0
            }
        
        return comparison
    
    def _compare_github(self, data1: List[Dict], data2: List[Dict]) -> Dict:
        """GitHub 데이터 비교"""
        import pandas as pd
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        comparison = {}
        
        if 'stars' in df1.columns and 'stars' in df2.columns:
            comparison['stars'] = {
                'session1_mean': float(df1['stars'].mean()),
                'session2_mean': float(df2['stars'].mean()),
                'change': float(df2['stars'].mean() - df1['stars'].mean()),
                'change_percent': float((df2['stars'].mean() - df1['stars'].mean()) / df1['stars'].mean() * 100) if df1['stars'].mean() > 0 else 0
            }
        
        if 'forks' in df1.columns and 'forks' in df2.columns:
            comparison['forks'] = {
                'session1_mean': float(df1['forks'].mean()),
                'session2_mean': float(df2['forks'].mean()),
                'change': float(df2['forks'].mean() - df1['forks'].mean()),
                'change_percent': float((df2['forks'].mean() - df1['forks'].mean()) / df1['forks'].mean() * 100) if df1['forks'].mean() > 0 else 0
            }
        
        return comparison
    
    def _compare_hackernews(self, data1: List[Dict], data2: List[Dict]) -> Dict:
        """HackerNews 데이터 비교"""
        import pandas as pd
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        comparison = {}
        
        if 'score' in df1.columns and 'score' in df2.columns:
            comparison['score'] = {
                'session1_mean': float(df1['score'].mean()),
                'session2_mean': float(df2['score'].mean()),
                'change': float(df2['score'].mean() - df1['score'].mean()),
                'change_percent': float((df2['score'].mean() - df1['score'].mean()) / df1['score'].mean() * 100) if df1['score'].mean() > 0 else 0
            }
        
        if 'descendants' in df1.columns and 'descendants' in df2.columns:
            comparison['comments'] = {
                'session1_mean': float(df1['descendants'].mean()),
                'session2_mean': float(df2['descendants'].mean()),
                'change': float(df2['descendants'].mean() - df1['descendants'].mean()),
                'change_percent': float((df2['descendants'].mean() - df1['descendants'].mean()) / df1['descendants'].mean() * 100) if df1['descendants'].mean() > 0 else 0
            }
        
        return comparison
    
    def get_trend_data(self, source: str, days: int = 7) -> List[Dict]:
        """
        최근 N일간의 트렌드 데이터 조회
        
        Args:
            source: 데이터 소스
            days: 조회할 일수
        
        Returns:
            일별 통계 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 최근 N일간의 세션 조회
        cursor.execute('''
            SELECT * FROM collection_sessions
            WHERE source = ? 
            AND collected_at >= datetime('now', '-' || ? || ' days')
            ORDER BY collected_at ASC
        ''', (source, days))
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        trend_data = []
        for session in sessions:
            session_data = self.get_session_data(session['id'], source)
            if not session_data:
                continue
            
            import pandas as pd
            df = pd.DataFrame(session_data)
            
            trend_item = {
                'date': session['collected_at'],
                'session_id': session['id'],
                'count': len(session_data)
            }
            
            # 소스별 통계 추가
            if source == 'reddit' and 'score' in df.columns:
                trend_item['avg_score'] = float(df['score'].mean())
                trend_item['avg_comments'] = float(df['num_comments'].mean()) if 'num_comments' in df.columns else 0
            elif source == 'github' and 'stars' in df.columns:
                trend_item['avg_stars'] = float(df['stars'].mean())
                trend_item['avg_forks'] = float(df['forks'].mean()) if 'forks' in df.columns else 0
            elif source == 'hackernews' and 'score' in df.columns:
                trend_item['avg_score'] = float(df['score'].mean())
                trend_item['avg_comments'] = float(df['descendants'].mean()) if 'descendants' in df.columns else 0
            
            trend_data.append(trend_item)
        
        return trend_data
    
    def get_statistics(self) -> Dict:
        """
        전체 데이터베이스 통계 조회
        
        Returns:
            통계 정보 딕셔너리
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 소스별 세션 수
        cursor.execute('''
            SELECT source, COUNT(*) as count 
            FROM collection_sessions 
            GROUP BY source
        ''')
        stats['sessions_by_source'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 소스별 총 데이터 수
        cursor.execute('SELECT COUNT(*) FROM reddit_posts')
        stats['total_reddit_posts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM github_repos')
        stats['total_github_repos'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM hackernews_stories')
        stats['total_hackernews_stories'] = cursor.fetchone()[0]
        
        # 최신 수집 시간
        cursor.execute('''
            SELECT source, MAX(collected_at) as last_collected
            FROM collection_sessions
            GROUP BY source
        ''')
        stats['last_collected'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return stats

