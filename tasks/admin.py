from django.contrib import admin
from .models import Project,Task, ProjectMember
from .models import ActivityLog

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):from .models import ActivityLog

list_display = ('name','manager','created_at')

@admin.register(Task) 
class TaskAdmin(admin.ModelAdmin):
         list_display = ('title','project','assigned_to','status','due_date')
         list_filter = ('status','project')

admin.site.register(ProjectMember) 
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'action', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('action', 'user__username')