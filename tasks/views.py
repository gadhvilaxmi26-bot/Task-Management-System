from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Task, ProjectMember, ActivityLog
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from .forms import TaskForm, ProjectMemberForm, TaskStatusUpdateForm, ProjectForm
User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    role = str(user.role).lower()
    if role == 'admin':
        tasks = Task.objects.all()
        projects = Project.objects.all()
    elif role == 'manager':
        tasks = Task.objects.filter(project__manager=user)
        projects = Project.objects.filter(manager=user)
    else: 
        tasks = Task.objects.filter(assigned_to=user)
        projects = Project.objects.filter(member__user=user).distinct()

    summary = {
        'total': tasks.count(),
        'todo': tasks.filter(status='TODO').count(),
        'in_progress': tasks.filter(status='IN_PROGRESS').count(),
        'done': tasks.filter(status='DONE').count(),
    }

    for project in projects:
        total = project.tasks.count()
        done = project.tasks.filter(status='DONE').count()
        project.progress_percentage = int((done / total) * 100) if total > 0 else 0

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks.order_by('-created_at')[:5], 
        'summary': summary,
        'user_projects': projects
    })

@login_required
def project_list(request):
    role = str(request.user.role).lower()
    if role == 'admin':
        projects = Project.objects.all()
    elif role == 'manager':
        projects = Project.objects.filter(manager=request.user)
    else: 
        projects = Project.objects.filter(member__user=request.user).distinct()
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
    activities = ActivityLog.objects.filter(project=project).order_by('-created_at')[:10]
    context = {
        'project': project,
        'tasks': tasks,
        'members': members,
        'activities': activities,
    }
    return render(request, 'tasks/project_detail.html', context)
@login_required
def add_project_member(request, pk):
    project = get_object_or_404(Project, id=pk)
    if request.method == "POST":
        form = ProjectMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectMemberForm()
        already_in = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
        form.fields['user'].queryset = User.objects.filter(role__iexact='developer').exclude(id__in=already_in)
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
    p_id = task.project.id
    task.delete()
    return redirect('project_detail', pk=p_id)
from django.contrib import messages
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