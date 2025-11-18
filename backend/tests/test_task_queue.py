"""Tests for task queue service"""

import pytest
from uuid import uuid4
from app.services.task_queue import TaskQueueService


class TestTaskQueueService:
    """Test TaskQueueService"""
    
    def test_start_verification(self):
        """Test starting a verification task"""
        company_id = uuid4()
        task_info = TaskQueueService.start_verification(company_id, timeout_hours=2.0)
        
        assert isinstance(task_info, dict)
        # May return None if Celery not configured, but should not crash
    
    def test_get_task_status(self):
        """Test getting task status"""
        task_id = "test-task-id"
        status = TaskQueueService.get_task_status(task_id)
        
        # Should return status dict or None
        assert status is None or isinstance(status, dict)
    
    def test_cancel_task(self):
        """Test canceling a task"""
        task_id = "test-task-id"
        result = TaskQueueService.cancel_task(task_id)
        
        # Should return success boolean or None
        assert result is None or isinstance(result, bool)

