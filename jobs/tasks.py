# tasks.py
from celery import shared_task
from .models import Task, TaskLog


@shared_task
def life_funeral_daily(task_id):
    task = Task.objects.get(pk=task_id)
    # Implement task 1 logic here
    task.status = "running"
    task.save()
    # Perform task 1 logic
    task.status = "completed"
    task.save()
    # Create a task log entry
    TaskLog.objects.create(task=task, status="completed")
