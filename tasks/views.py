from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Task, ProjectMember
from .forms import ProjectForm, ProjectMemberForm, TaskForm 
from django.http import HttpResponseForbidden

@login_required
def dashboard(request):
    user = request.user
    role = str(user.role).lower()

    if role == 'admin':
        tasks = Task.objects.all()
    elif role == 'manager':
        tasks = Task.objects.filter(project__manager=user)
    else: # Developer
        tasks = Task.objects.filter(assigned_to=user)

    summary = {
        'total': tasks.count(),
        'todo': tasks.filter(status='TODO').count(),
        'in_progress': tasks.filter(status='IN_PROGRESS').count(),
        'done': tasks.filter(status='DONE').count(),
    }

    # Developer ke liye uske projects
    user_projects = Project.objects.filter(member__user=user).distinct()

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks[:5], 
        'summary': summary,
        'user_projects': user_projects
    })

@login_required
def project_list(request):
    user_role = str(request.user.role).lower()
    if user_role == 'admin':
        projects = Project.objects.all()
    elif user_role == 'manager':
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
    
    form = ProjectMemberForm()
    if request.method == "POST":
        if str(request.user.role).lower() in ['admin', 'manager']:
            form = ProjectMemberForm(request.POST)
            if form.is_valid():
                member = form.save(commit=False)
                member.project = project
                member.save()
                return redirect('project_detail', pk=project.pk)
    
    return render(request, 'tasks/project_detail.html', {
        'project': project, 'members': members, 'tasks': tasks, 'form': form
    })

@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()

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
        from django.contrib.auth import get_user_model
        User = get_user_model()
        form.fields['assigned_to'].queryset = User.objects.filter(id__in=member_ids)

    return render(request, 'tasks/task_form.html', {'form': form, 'project': project, 'title': 'Create Task'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Developer status badal sakta hai, Manager sab badal sakta hai
    if request.user != task.assigned_to and request.user != task.project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=task.project.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'title': 'Update Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user != task.project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()
    
    p_id = task.project.id
    task.delete()
    return redirect('project_detail', pk=p_id)

@login_required
def remove_member(request, pk):
    member = get_object_or_404(ProjectMember, pk=pk)
    if request.user != member.project.manager and str(request.user.role).lower() != 'admin':
        return HttpResponseForbidden()
    
    p_id = member.project.id
    member.delete()
    return redirect('project_detail', pk=p_id)