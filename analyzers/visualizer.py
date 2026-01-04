"""
데이터 시각화 모듈
수집 및 분석된 데이터를 시각화합니다.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
import config

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

sns.set_style("whitegrid")


class Visualizer:
    """데이터 시각화를 수행하는 클래스"""
    
    def __init__(self):
        self.output_dir = Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def visualize(self, data, analysis_results=None, source=None):
        """
        데이터 시각화
        
        Args:
            data: 시각화할 데이터 리스트
            analysis_results: 분석 결과 (선택사항)
            source: 데이터 소스
        """
        if not data:
            print("⚠️  시각화할 데이터가 없습니다.")
            return
        
        if source is None:
            source = data[0].get('source', 'unknown') if data else 'unknown'
        
        print(f"📈 데이터 시각화 중: {source}")
        
        df = pd.DataFrame(data)
        
        # 소스별 시각화
        if source == 'reddit':
            self._visualize_reddit(df)
        elif source == 'github':
            self._visualize_github(df)
        elif source == 'hackernews':
            self._visualize_hackernews(df)
    
    def _visualize_reddit(self, df):
        """Reddit 데이터 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=config.FIGURE_SIZE)
        fig.suptitle('Reddit 데이터 분석', fontsize=16, fontweight='bold')
        
        # 1. 점수 분포
        if 'score' in df.columns:
            axes[0, 0].hist(df['score'], bins=30, edgecolor='black', alpha=0.7)
            axes[0, 0].set_title('점수 분포')
            axes[0, 0].set_xlabel('점수')
            axes[0, 0].set_ylabel('빈도')
        
        # 2. 댓글 수 분포
        if 'num_comments' in df.columns:
            axes[0, 1].hist(df['num_comments'], bins=30, edgecolor='black', alpha=0.7, color='orange')
            axes[0, 1].set_title('댓글 수 분포')
            axes[0, 1].set_xlabel('댓글 수')
            axes[0, 1].set_ylabel('빈도')
        
        # 3. 점수 vs 댓글 수
        if 'score' in df.columns and 'num_comments' in df.columns:
            axes[1, 0].scatter(df['score'], df['num_comments'], alpha=0.5)
            axes[1, 0].set_title('점수 vs 댓글 수')
            axes[1, 0].set_xlabel('점수')
            axes[1, 0].set_ylabel('댓글 수')
        
        # 4. 서브레딧 분포 (상위 10개)
        if 'subreddit' in df.columns:
            subreddit_counts = df['subreddit'].value_counts().head(10)
            axes[1, 1].barh(range(len(subreddit_counts)), subreddit_counts.values)
            axes[1, 1].set_yticks(range(len(subreddit_counts)))
            axes[1, 1].set_yticklabels(subreddit_counts.index)
            axes[1, 1].set_title('서브레딧 분포 (상위 10개)')
            axes[1, 1].set_xlabel('게시물 수')
        
        plt.tight_layout()
        self._save_figure(fig, 'reddit_analysis')
    
    def _visualize_github(self, df):
        """GitHub 데이터 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=config.FIGURE_SIZE)
        fig.suptitle('GitHub 데이터 분석', fontsize=16, fontweight='bold')
        
        # 1. 스타 수 분포
        if 'stars' in df.columns:
            axes[0, 0].hist(df['stars'], bins=30, edgecolor='black', alpha=0.7)
            axes[0, 0].set_title('스타 수 분포')
            axes[0, 0].set_xlabel('스타 수')
            axes[0, 0].set_ylabel('빈도')
            axes[0, 0].set_yscale('log')
        
        # 2. 포크 수 분포
        if 'forks' in df.columns:
            axes[0, 1].hist(df['forks'], bins=30, edgecolor='black', alpha=0.7, color='green')
            axes[0, 1].set_title('포크 수 분포')
            axes[0, 1].set_xlabel('포크 수')
            axes[0, 1].set_ylabel('빈도')
            axes[0, 1].set_yscale('log')
        
        # 3. 스타 vs 포크
        if 'stars' in df.columns and 'forks' in df.columns:
            axes[1, 0].scatter(df['stars'], df['forks'], alpha=0.5)
            axes[1, 0].set_title('스타 vs 포크')
            axes[1, 0].set_xlabel('스타 수')
            axes[1, 0].set_ylabel('포크 수')
            axes[1, 0].set_xscale('log')
            axes[1, 0].set_yscale('log')
        
        # 4. 언어 분포 (상위 10개)
        if 'language' in df.columns:
            language_counts = df['language'].value_counts().head(10)
            axes[1, 1].barh(range(len(language_counts)), language_counts.values, color='purple')
            axes[1, 1].set_yticks(range(len(language_counts)))
            axes[1, 1].set_yticklabels(language_counts.index)
            axes[1, 1].set_title('언어 분포 (상위 10개)')
            axes[1, 1].set_xlabel('저장소 수')
        
        plt.tight_layout()
        self._save_figure(fig, 'github_analysis')
    
    def _visualize_hackernews(self, df):
        """HackerNews 데이터 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=config.FIGURE_SIZE)
        fig.suptitle('HackerNews 데이터 분석', fontsize=16, fontweight='bold')
        
        # 1. 점수 분포
        if 'score' in df.columns:
            axes[0, 0].hist(df['score'], bins=30, edgecolor='black', alpha=0.7)
            axes[0, 0].set_title('점수 분포')
            axes[0, 0].set_xlabel('점수')
            axes[0, 0].set_ylabel('빈도')
        
        # 2. 댓글 수 분포
        if 'descendants' in df.columns:
            axes[0, 1].hist(df['descendants'], bins=30, edgecolor='black', alpha=0.7, color='red')
            axes[0, 1].set_title('댓글 수 분포')
            axes[0, 1].set_xlabel('댓글 수')
            axes[0, 1].set_ylabel('빈도')
        
        # 3. 점수 vs 댓글 수
        if 'score' in df.columns and 'descendants' in df.columns:
            axes[1, 0].scatter(df['score'], df['descendants'], alpha=0.5)
            axes[1, 0].set_title('점수 vs 댓글 수')
            axes[1, 0].set_xlabel('점수')
            axes[1, 0].set_ylabel('댓글 수')
        
        # 4. 상위 스토리 (점수 기준 상위 10개)
        if 'score' in df.columns and 'title' in df.columns:
            top_stories = df.nlargest(10, 'score')
            axes[1, 1].barh(range(len(top_stories)), top_stories['score'].values)
            axes[1, 1].set_yticks(range(len(top_stories)))
            # 제목이 너무 길면 잘라서 표시
            titles = [title[:30] + '...' if len(title) > 30 else title 
                     for title in top_stories['title'].values]
            axes[1, 1].set_yticklabels(titles, fontsize=8)
            axes[1, 1].set_title('상위 스토리 (점수 기준)')
            axes[1, 1].set_xlabel('점수')
        
        plt.tight_layout()
        self._save_figure(fig, 'hackernews_analysis')
    
    def _save_figure(self, fig, name):
        """그래프를 파일로 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = self.output_dir / filename
        
        fig.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
        print(f"📊 시각화 저장: {filepath}")
        plt.close(fig)

