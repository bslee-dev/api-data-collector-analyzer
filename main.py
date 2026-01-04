"""
API Data Collector & Analyzer
메인 실행 스크립트
"""

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from collectors import RedditCollector, GitHubCollector, HackerNewsCollector
from analyzers import DataAnalyzer, Visualizer
from database import DatabaseManager
import config


def collect_reddit(limit=None, db_manager=None):
    """Reddit 데이터 수집"""
    collector = RedditCollector()
    limit = limit or config.DEFAULT_LIMIT
    data = collector.collect(subreddit=config.REDDIT_SUBREDDIT, limit=limit)
    if data:
        collector.save(data)
        # 데이터베이스 저장
        if config.ENABLE_DATABASE and db_manager:
            db_manager.save_collection(data, 'reddit')
    return data


def collect_github(limit=None, db_manager=None):
    """GitHub 데이터 수집"""
    collector = GitHubCollector()
    limit = limit or config.DEFAULT_LIMIT
    data = collector.collect(language=config.GITHUB_LANGUAGE, limit=limit)
    if data:
        collector.save(data)
        # 데이터베이스 저장
        if config.ENABLE_DATABASE and db_manager:
            db_manager.save_collection(data, 'github')
    return data


def collect_hackernews(limit=None, db_manager=None):
    """HackerNews 데이터 수집"""
    collector = HackerNewsCollector()
    limit = limit or config.HACKERNEWS_LIMIT
    data = collector.collect(limit=limit)
    if data:
        collector.save(data)
        # 데이터베이스 저장
        if config.ENABLE_DATABASE and db_manager:
            db_manager.save_collection(data, 'hackernews')
    return data


def analyze_data(data, source):
    """데이터 분석"""
    analyzer = DataAnalyzer()
    results = analyzer.analyze(data, source=source)
    analyzer.save_results(results)
    return results


def visualize_data(data, source):
    """데이터 시각화"""
    visualizer = Visualizer()
    visualizer.visualize(data, source=source)


def main():
    parser = argparse.ArgumentParser(
        description='API Data Collector & Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py                    # 모든 소스에서 데이터 수집 및 분석
  python main.py --source reddit    # Reddit만 수집
  python main.py --source github    # GitHub만 수집
  python main.py --analyze-only     # 이미 수집된 데이터 분석만 수행
        """
    )
    
    parser.add_argument(
        '--source',
        choices=['reddit', 'github', 'hackernews', 'all'],
        default='all',
        help='수집할 데이터 소스 (기본값: all)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=config.DEFAULT_LIMIT,
        help=f'수집할 데이터 수 (기본값: {config.DEFAULT_LIMIT})'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='데이터 수집 없이 분석만 수행 (기존 데이터 사용)'
    )
    
    parser.add_argument(
        '--no-visualize',
        action='store_true',
        help='시각화 생략'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='이전 데이터와 비교 분석 수행'
    )
    
    parser.add_argument(
        '--db-stats',
        action='store_true',
        help='데이터베이스 통계 조회'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 API Data Collector & Analyzer")
    print("=" * 60)
    print()
    
    # 데이터베이스 관리자 초기화
    db_manager = None
    if config.ENABLE_DATABASE:
        try:
            db_manager = DatabaseManager()
        except Exception as e:
            print(f"⚠️  데이터베이스 초기화 실패: {e}")
            print("   JSON 파일 저장만 진행합니다.")
    
    # 데이터베이스 통계 조회
    if args.db_stats:
        if db_manager:
            stats = db_manager.get_statistics()
            print("\n📊 데이터베이스 통계")
            print("=" * 60)
            print(f"소스별 세션 수:")
            for source, count in stats.get('sessions_by_source', {}).items():
                print(f"  {source}: {count}개")
            print(f"\n총 데이터 수:")
            print(f"  Reddit 게시물: {stats.get('total_reddit_posts', 0)}개")
            print(f"  GitHub 저장소: {stats.get('total_github_repos', 0)}개")
            print(f"  HackerNews 스토리: {stats.get('total_hackernews_stories', 0)}개")
            print(f"\n최신 수집 시간:")
            for source, last_time in stats.get('last_collected', {}).items():
                print(f"  {source}: {last_time}")
        else:
            print("❌ 데이터베이스가 활성화되지 않았습니다.")
        return
    
    if args.analyze_only:
        print("📊 분석 모드: 기존 데이터 분석")
        # TODO: 기존 데이터 로드 기능 추가
        print("⚠️  분석 모드는 아직 구현되지 않았습니다.")
        return
    
    # 데이터 수집
    sources_to_collect = []
    if args.source == 'all':
        sources_to_collect = ['reddit', 'github', 'hackernews']
    else:
        sources_to_collect = [args.source]
    
    all_data = {}
    
    for source in sources_to_collect:
        print(f"\n{'='*60}")
        print(f"📥 {source.upper()} 데이터 수집 시작")
        print(f"{'='*60}\n")
        
        try:
            if source == 'reddit':
                data = collect_reddit(args.limit, db_manager)
            elif source == 'github':
                data = collect_github(args.limit, db_manager)
            elif source == 'hackernews':
                data = collect_hackernews(args.limit, db_manager)
            else:
                continue
            
            if data:
                all_data[source] = data
                
                # 이전 데이터와 비교
                if args.compare and db_manager:
                    print(f"\n{'='*60}")
                    print(f"🔍 {source.upper()} 이전 데이터와 비교")
                    print(f"{'='*60}\n")
                    latest_session = db_manager.get_latest_session(source)
                    if latest_session:
                        sessions = db_manager.get_recent_sessions(source, limit=2)
                        if len(sessions) >= 2:
                            comparison = db_manager.compare_sessions(
                                source, sessions[1]['id'], sessions[0]['id']
                            )
                            print(f"세션 비교 결과:")
                            print(f"  이전 세션: {sessions[1]['collected_at']} ({sessions[1]['item_count']}개)")
                            print(f"  현재 세션: {sessions[0]['collected_at']} ({sessions[0]['item_count']}개)")
                            print(f"  데이터 수 변화: {comparison.get('count_change', 0)}개 ({comparison.get('count_change_percent', 0):.2f}%)")
                            
                            if source == 'reddit' and 'score' in comparison:
                                score_info = comparison['score']
                                print(f"  평균 점수 변화: {score_info.get('change', 0):.2f} ({score_info.get('change_percent', 0):.2f}%)")
                            elif source == 'github' and 'stars' in comparison:
                                stars_info = comparison['stars']
                                print(f"  평균 스타 수 변화: {stars_info.get('change', 0):.2f} ({stars_info.get('change_percent', 0):.2f}%)")
                            elif source == 'hackernews' and 'score' in comparison:
                                score_info = comparison['score']
                                print(f"  평균 점수 변화: {score_info.get('change', 0):.2f} ({score_info.get('change_percent', 0):.2f}%)")
                
                # 분석
                print(f"\n{'='*60}")
                print(f"📊 {source.upper()} 데이터 분석")
                print(f"{'='*60}\n")
                results = analyze_data(data, source)
                
                # 시각화
                if not args.no_visualize:
                    print(f"\n{'='*60}")
                    print(f"📈 {source.upper()} 데이터 시각화")
                    print(f"{'='*60}\n")
                    visualize_data(data, source)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ {source} 데이터 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 요약
    print(f"\n{'='*60}")
    print("✅ 작업 완료 요약")
    print(f"{'='*60}")
    for source, data in all_data.items():
        print(f"  {source}: {len(data)}개 데이터 수집 및 분석 완료")
    print(f"\n📁 데이터 저장 위치:")
    print(f"  - 원본 데이터: {config.RAW_DATA_DIR}")
    print(f"  - 분석 결과: outputs/")
    print(f"  - 시각화: outputs/")
    if config.ENABLE_DATABASE and db_manager:
        print(f"  - 데이터베이스: {config.DB_PATH}")


if __name__ == '__main__':
    main()

