"""
작업 스케줄러
APScheduler를 사용하여 주기적 데이터 수집 작업을 관리합니다.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import config


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """작업 스케줄러 클래스"""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 60):
        """
        스케줄러 초기화
        
        Args:
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 대기 시간 (초)
        """
        self.scheduler = BackgroundScheduler()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.job_retries = {}  # 작업별 재시도 횟수 추적
        
        # 이벤트 리스너 등록
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        logger.info("스케줄러 초기화 완료")
    
    def _job_listener(self, event):
        """작업 실행 이벤트 리스너"""
        if event.exception:
            job_id = event.job_id
            logger.error(f"작업 '{job_id}' 실행 중 오류 발생: {event.exception}")
            
            # 재시도 로직
            if job_id not in self.job_retries:
                self.job_retries[job_id] = 0
            
            if self.job_retries[job_id] < self.max_retries:
                self.job_retries[job_id] += 1
                logger.info(f"작업 '{job_id}' 재시도 ({self.job_retries[job_id]}/{self.max_retries})")
                
                # 재시도 작업 스케줄링
                retry_time = datetime.now() + timedelta(seconds=self.retry_delay)
                self.scheduler.add_job(
                    func=event.job.func,
                    trigger='date',
                    run_date=retry_time,
                    id=f"{job_id}_retry_{self.job_retries[job_id]}",
                    args=event.job.args,
                    kwargs=event.job.kwargs
                )
            else:
                logger.error(f"작업 '{job_id}' 최대 재시도 횟수 초과. 작업 중단.")
                self.job_retries[job_id] = 0  # 재시도 카운터 리셋
        else:
            # 성공 시 재시도 카운터 리셋
            job_id = event.job_id
            if job_id in self.job_retries:
                self.job_retries[job_id] = 0
                logger.info(f"작업 '{job_id}' 성공적으로 완료")
    
    def add_daily_job(
        self,
        func: Callable,
        hour: int = 0,
        minute: int = 0,
        job_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> str:
        """
        매일 실행되는 작업 추가
        
        Args:
            func: 실행할 함수
            hour: 실행 시간 (0-23)
            minute: 실행 분 (0-59)
            job_id: 작업 ID (기본값: 함수 이름)
            *args, **kwargs: 함수에 전달할 인자
        
        Returns:
            작업 ID
        """
        if job_id is None:
            job_id = f"{func.__name__}_daily"
        
        trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            args=args,
            kwargs=kwargs,
            replace_existing=True
        )
        
        logger.info(f"매일 작업 추가: {job_id} (시간: {hour:02d}:{minute:02d})")
        return job_id
    
    def add_interval_job(
        self,
        func: Callable,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
        seconds: Optional[int] = None,
        job_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> str:
        """
        주기적으로 실행되는 작업 추가
        
        Args:
            func: 실행할 함수
            hours: 간격 (시간)
            minutes: 간격 (분)
            seconds: 간격 (초)
            job_id: 작업 ID (기본값: 함수 이름)
            *args, **kwargs: 함수에 전달할 인자
        
        Returns:
            작업 ID
        """
        if job_id is None:
            job_id = f"{func.__name__}_interval"
        
        if hours:
            trigger = IntervalTrigger(hours=hours)
        elif minutes:
            trigger = IntervalTrigger(minutes=minutes)
        elif seconds:
            trigger = IntervalTrigger(seconds=seconds)
        else:
            raise ValueError("hours, minutes, 또는 seconds 중 하나를 지정해야 합니다.")
        
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            args=args,
            kwargs=kwargs,
            replace_existing=True
        )
        
        interval_str = f"{hours}시간" if hours else f"{minutes}분" if minutes else f"{seconds}초"
        logger.info(f"주기적 작업 추가: {job_id} (간격: {interval_str})")
        return job_id
    
    def add_cron_job(
        self,
        func: Callable,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        week: Optional[int] = None,
        day_of_week: Optional[str] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        job_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> str:
        """
        Cron 형식으로 작업 추가
        
        Args:
            func: 실행할 함수
            year, month, day, week, day_of_week, hour, minute, second: Cron 파라미터
            job_id: 작업 ID (기본값: 함수 이름)
            *args, **kwargs: 함수에 전달할 인자
        
        Returns:
            작업 ID
        """
        if job_id is None:
            job_id = f"{func.__name__}_cron"
        
        trigger = CronTrigger(
            year=year,
            month=month,
            day=day,
            week=week,
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            second=second
        )
        
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            args=args,
            kwargs=kwargs,
            replace_existing=True
        )
        
        logger.info(f"Cron 작업 추가: {job_id}")
        return job_id
    
    def remove_job(self, job_id: str):
        """작업 제거"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"작업 제거: {job_id}")
        except Exception as e:
            logger.error(f"작업 제거 실패 ({job_id}): {e}")
    
    def get_jobs(self) -> list:
        """등록된 모든 작업 목록 조회"""
        return self.scheduler.get_jobs()
    
    def start(self):
        """스케줄러 시작"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("스케줄러 시작됨")
        else:
            logger.warning("스케줄러가 이미 실행 중입니다.")
    
    def stop(self):
        """스케줄러 중지"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("스케줄러 중지됨")
        else:
            logger.warning("스케줄러가 실행 중이 아닙니다.")
    
    def pause(self):
        """스케줄러 일시 중지"""
        if self.scheduler.running:
            self.scheduler.pause()
            logger.info("스케줄러 일시 중지됨")
    
    def resume(self):
        """스케줄러 재개"""
        if self.scheduler.running:
            self.scheduler.resume()
            logger.info("스케줄러 재개됨")
    
    def is_running(self) -> bool:
        """스케줄러 실행 상태 확인"""
        return self.scheduler.running


def create_collection_job_wrapper(collect_func: Callable, source: str, limit: int = None):
    """
    수집 함수를 래핑하여 재시도 로직과 로깅을 추가
    
    Args:
        collect_func: 수집 함수
        source: 데이터 소스 이름
        limit: 수집 제한
    
    Returns:
        래핑된 함수
    """
    def wrapper():
        try:
            logger.info(f"[{source}] 데이터 수집 시작")
            result = collect_func(limit=limit)
            if result:
                logger.info(f"[{source}] 데이터 수집 완료: {len(result)}개 항목")
            else:
                logger.warning(f"[{source}] 데이터 수집 결과 없음")
            return result
        except Exception as e:
            logger.error(f"[{source}] 데이터 수집 실패: {e}", exc_info=True)
            raise
    
    wrapper.__name__ = f"collect_{source}"
    return wrapper

