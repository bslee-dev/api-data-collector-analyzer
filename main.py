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
import config


def collect_reddit(limit=None):
    """Reddit 데이터 수집"""
    collector = RedditCollector()
    limit = limit or config.DEFAULT_LIMIT
    data = collector.collect(subreddit=config.REDDIT_SUBREDDIT, limit=limit)
    if data:
        collector.save(data)
    return data


def collect_github(limit=None):
    """GitHub 데이터 수집"""
    collector = GitHubCollector()
    limit = limit or config.DEFAULT_LIMIT
    data = collector.collect(language=config.GITHUB_LANGUAGE, limit=limit)
    if data:
        collector.save(data)
    return data


def collect_hackernews(limit=None):
    """HackerNews 데이터 수집"""
    collector = HackerNewsCollector()
    limit = limit or config.HACKERNEWS_LIMIT
    data = collector.collect(limit=limit)
    if data:
        collector.save(data)
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
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 API Data Collector & Analyzer")
    print("=" * 60)
    print()
    
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
                data = collect_reddit(args.limit)
            elif source == 'github':
                data = collect_github(args.limit)
            elif source == 'hackernews':
                data = collect_hackernews(args.limit)
            else:
                continue
            
            if data:
                all_data[source] = data
                
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


if __name__ == '__main__':
    main()

