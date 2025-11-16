"""Task queue management service"""

from typing import Optional, Dict
from uuid import UUID
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.tasks.analysis_tasks import verify_company_task, get_verification_status_task, cancel_verification_task


class TaskQueueService:
    """Service for managing verification task queue"""
    
    @staticmethod
    def start_verification(company_id: UUID, timeout_hours: float = 2.0) -> Dict:
        """
        Start async verification task
        
        Args:
            company_id: Company ID to verify
            timeout_hours: Maximum time for verification
        
        Returns:
            Dictionary with task information
        """
        task = verify_company_task.delay(str(company_id), timeout_hours)
        
        return {
            "task_id": task.id,
            "company_id": str(company_id),
            "status": "queued",
            "timeout_hours": timeout_hours
        }
    
    @staticmethod
    def get_task_status(task_id: str) -> Dict:
        """
        Get status of a verification task
        
        Args:
            task_id: Celery task ID
        
        Returns:
            Dictionary with task status information
        """
        result = AsyncResult(task_id, app=celery_app)
        
        status_info = {
            "task_id": task_id,
            "status": result.state,
            "ready": result.ready(),
        }
        
        if result.ready():
            if result.successful():
                status_info["result"] = result.result
                status_info["verification_result_id"] = result.result
            else:
                status_info["error"] = str(result.info) if result.info else "Task failed"
        else:
            # Task is still pending or in progress
            if result.state == "PENDING":
                status_info["message"] = "Task is waiting to be processed"
            elif result.state == "STARTED":
                status_info["message"] = "Task is currently being processed"
            elif result.state == "RETRY":
                status_info["message"] = "Task is being retried"
            elif result.state == "REVOKED":
                status_info["message"] = "Task was cancelled"
        
        return status_info
    
    @staticmethod
    def cancel_task(task_id: str) -> Dict:
        """
        Cancel a verification task
        
        Args:
            task_id: Celery task ID
        
        Returns:
            Dictionary with cancellation status
        """
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancellation requested"
        }
    
    @staticmethod
    def get_queue_stats() -> Dict:
        """
        Get statistics about the task queue
        
        Returns:
            Dictionary with queue statistics
        """
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active = inspect.active()
        # Get scheduled tasks
        scheduled = inspect.scheduled()
        # Get reserved tasks
        reserved = inspect.reserved()
        
        total_active = sum(len(tasks) for tasks in (active or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled or {}).values())
        total_reserved = sum(len(tasks) for tasks in (reserved or {}).values())
        
        return {
            "active_tasks": total_active,
            "scheduled_tasks": total_scheduled,
            "reserved_tasks": total_reserved,
            "total_pending": total_active + total_scheduled + total_reserved
        }
    
    @staticmethod
    def get_worker_stats() -> Dict:
        """
        Get statistics about Celery workers
        
        Returns:
            Dictionary with worker statistics
        """
        inspect = celery_app.control.inspect()
        
        # Get registered workers
        registered = inspect.registered()
        # Get active workers
        stats = inspect.stats()
        
        worker_count = len(stats) if stats else 0
        registered_tasks = {}
        
        if registered:
            for worker, tasks in registered.items():
                registered_tasks[worker] = len(tasks) if tasks else 0
        
        return {
            "worker_count": worker_count,
            "workers": list(stats.keys()) if stats else [],
            "registered_tasks": registered_tasks
        }

