from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Task, ProjectMember, ActivityLog, Comment, Notification
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from .forms import TaskForm, ProjectMemberForm, TaskStatusUpdateForm, ProjectForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from rest_framework import viewsets
from .serializers import TaskSerializer

User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    role = str(user.role).lower()
    
    if role == 'admin':
        tasks = Task.objects.all()
        user_projects = Project.objects.all()
    elif role == 'manager':
        tasks = Task.objects.filter(project__manager=user)
        user_projects = Project.objects.filter(manager=user)
    else: 
        tasks = Task.objects.filter(assigned_to=user)
        user_projects = Project.objects.filter(members__user=user).distinct()

    summary = {
        'total': tasks.count(),
        'todo': tasks.filter(status='TODO').count(),
        'in_progress': tasks.filter(status='IN_PROGRESS').count(),
        'in_review': tasks.filter(status='IN_REVIEW').count(), 
        'done': tasks.filter(status='DONE').count(),
    }

    for project in user_projects:
        total = project.tasks.count()
        done = project.tasks.filter(status='DONE').count()
        project.progress_percentage = int((done / total) * 100) if total > 0 else 0

    overdue_tasks = tasks.filter(due_date__lt=timezone.now().date()).exclude(status='DONE') 
    
    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks.order_by('-created_at')[:5], 
        'summary': summary,
        'user_projects': user_projects, 
        'overdue_tasks': overdue_tasks,
        'chart_data': [summary['todo'], summary['in_progress'], summary['in_review'], summary['done']]
    })

@login_required
def project_list(request):
    role = str(request.user.role).lower()

    if role == 'admin':
        projects = Project.objects.all()
    elif role == 'manager':
        projects = Project.objects.filter(manager=request.user)
    else: 
        projects = Project.objects.filter(members__user=request.user).distinct()   
    return render(request, 'tasks/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if str(request.user.role).lower() not in ['admin', 'manager']:
        return HttpResponseForbidden("Access Denied")
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Create New Project'})

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Update Project'})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()
    if request.method == "POST":
        project.delete()
        return redirect('project_list')
    return render(request, 'tasks/project_confirm_delete.html', {'project': project})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    members = ProjectMember.objects.filter(project=project)
    
    tasks = Task.objects.filter(project=project)
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')      
    priority_filter = request.GET.get('priority', '')   
    
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    activities = ActivityLog.objects.filter(project=project).order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'tasks': tasks,
        'members': members,
        'activities': activities,
        'search_query': search_query,
        'status_filter': status_filter,   
        'priority_filter': priority_filter,
    }
    return render(request, 'tasks/project_detail.html', context)

@login_required
def add_project_member(request, pk):
    project = get_object_or_404(Project, id=pk)
    
    if not (request.user == project.manager or request.user.is_superuser):
        messages.error(request, "Only the manager can add members.")
        return redirect('project_detail', pk=pk)

    if request.method == "POST":
        form = ProjectMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()
        
            ActivityLog.objects.create(
                user=request.user, 
                project=project, 
                action=f"added {member.user.username} as {member.role_in_project} to the team"
            )
            messages.success(request, f"{member.user.username} added successfully!")
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectMemberForm()
        already_in = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
        form.fields['user'].queryset = User.objects.exclude(id__in=already_in)
        
    return render(request, 'tasks/add_member_form.html', {'form': form, 'project': project})

@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            ActivityLog.objects.create(user=request.user, project=project, action=f"created a new task: {task.title}")
            return redirect('project_detail', pk=project.id)
    else:
        form = TaskForm()
        member_ids = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
        if member_ids.exists():
            form.fields['assigned_to'].queryset = User.objects.filter(id__in=member_ids)
        else:
            form.fields['assigned_to'].queryset = User.objects.filter(role__iexact='developer')
    return render(request, 'tasks/task_form.html', {'form': form, 'project': project, 'title': 'Create Task'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user != task.assigned_to and request.user != task.project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                project=task.project,
                user=request.user,
                action=f"Edited task details for '{task.title}'"
            )
            
            return redirect('project_detail', pk=task.project.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'title': 'Update Task'})

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        old_status = task.get_status_display()
        form = TaskStatusUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            new_status = task.get_status_display()
            ActivityLog.objects.create(
                project=task.project,
                user=request.user,
                action=f"Updated task '{task.title}' status from {old_status} to {new_status}"
            )
            notify_user = task.project.manager 
            Notification.objects.create(
                user=task.created_by,
                message=f"Task '{task.title}' is now {new_status}. Please review it.",
                is_read=False
            )

            return redirect('project_detail', pk=task.project.id)
    else:
        form = TaskStatusUpdateForm(instance=task)
    
    return render(request, 'tasks/update_task_status.html', {
        'form': form,
        'task': task
    })

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if not (request.user == task.project.manager or request.user.is_superuser):
        messages.error(request, "You don't have permission to delete this task.")
        return redirect('project_detail', pk=task.project.pk)

    if request.method == "POST": 
        project_id = task.project.id
        task_title = task.title
        task.delete()
        ActivityLog.objects.create(user=request.user, project_id=project_id, action=f"deleted task: {task_title}")
        messages.success(request, "Task deleted successfully.")
        return redirect('project_detail', pk=project_id)
    
    return render(request, 'task_confirm_delete.html', {'task': task})

@login_required
def remove_member(request, pk):
    member = get_object_or_404(ProjectMember, id=pk)
    project_id = member.project.id
    
    if member.project.manager == request.user or request.user.is_staff:
        member.delete()
        messages.success(request, "Member removed successfully.")
        
        ActivityLog.objects.create(
            project=member.project,
            user=request.user,
            action=f"Removed member '{member.user.username}' from the project."
        )
    else:
        messages.error(request, "You don't have permission to remove members.")
        
    return redirect('project_detail', pk=project_id)

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    return render(request, 'index.html')

@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Comment.objects.create(task=task, author=request.user, content=content)
            if task.assigned_to and task.assigned_to != request.user:
                Notification.objects.create(
                    user=task.assigned_to,
                    message=f"{request.user.username} commented on your task: {task.title}"
                )
    return redirect('project_detail', pk=task.project.id)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer