from django.db import models
from celery import current_app
from jobs.enums import Processes


class Task(models.Model):
    title = models.CharField(max_length=100)
    task = models.CharField(
        max_length=30, choices=[(status.name, status.value) for status in Processes]
    )
    description = models.TextField()
    cron_schedule = models.CharField(
        max_length=50
    )  # Store the cron schedule as a string eg '30 2 * * *'
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        app = current_app._get_current_object()

        # Dynamically add the task to CELERY_BEAT_SCHEDULE
        app.conf.beat_schedule[f"task_{self.pk}"] = {
            "task": f"jobs.tasks.{self.task}",
            "schedule": self.cron_schedule,  # Use the cron schedule from the model
            "args": (self.pk,),
        }


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.TextField(null=True, blank=True)
    manual_run = models.BooleanField(default=False)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.task.title} - {self.status} - {self.timestamp}"
