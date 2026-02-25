from django.contrib import admin
from .models import Project, Task, ProjectMember, ActivityLog

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'created_at')
    list_filter = ('status',) 
    search_fields = ('name',)

@admin.register(Task) 
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'project')
    search_fields = ('title',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'action', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('action', 'user__username')

admin.site.register(ProjectMember)