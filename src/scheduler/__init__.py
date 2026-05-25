"""
Scheduler - APScheduler for cron-based DAG orchestration
SPEC.md Section 3: Scheduling layer
"""
import logging
from typing import Dict, Callable, Any, Optional, Tuple
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """APScheduler-based workflow scheduler for cron/hours-based orchestration"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Workflow scheduler initialized")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")

    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        cron_expr: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ) -> bool:
        """
        Add a cron-based job
        cron_expr: minute hour day month day_of_week
        e.g., "0 * * * *" = every hour
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            self.logger.error(f"Invalid cron expression: {cron_expr}")
            return False

        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )

        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            args=args or tuple(),
            kwargs=kwargs or {},
            replace_existing=True,
        )
        self.jobs[job_id] = job
        self.logger.info(f"Added cron job: {job_id}, schedule: {cron_expr}")
        return True

    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        interval_seconds: int,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ) -> bool:
        """Add an interval-based job"""
        trigger = IntervalTrigger(seconds=interval_seconds)
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            args=args or tuple(),
            kwargs=kwargs or {},
            replace_existing=True,
        )
        self.jobs[job_id] = job
        self.logger.info(f"Added interval job: {job_id}, interval: {interval_seconds}s")
        return True

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            self.logger.info(f"Removed job: {job_id}")
            return True
        return False

    def get_job(self, job_id: str) -> Optional[Any]:
        """Get job details"""
        return self.jobs.get(job_id)

    def list_jobs(self) -> Dict[str, Any]:
        """List all scheduled jobs"""
        return {job_id: str(job) for job_id, job in self.jobs.items()}


# Global scheduler instance
_scheduler: Optional[WorkflowScheduler] = None


def get_scheduler() -> WorkflowScheduler:
    """Get global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = WorkflowScheduler()
    return _scheduler