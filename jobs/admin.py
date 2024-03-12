# admin.py
from django.contrib import admin
from .models import Task, TaskLog

admin.site.register(Task)
admin.site.register(TaskLog)
