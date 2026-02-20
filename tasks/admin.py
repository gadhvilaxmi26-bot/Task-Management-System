from django.contrib import admin
from .models import Project,Task, ProjectMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','manager','created_at')

@admin.register(Task) 
class TaskAdmin(admin.ModelAdmin):
         list_display = ('title','project','assigned_to','status','due_date')
         list_filter = ('status','project')

admin.site.register(ProjectMember) 