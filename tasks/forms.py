from django import forms
from .models import Project, Task, ProjectMember
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # 'manager' ko yahan se hata diya hai kyunki wo hum views mein auto-add karte hain
        fields = ['name', 'description', 'status', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project ka naam...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kuch details...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ['user', 'role_in_project']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role_in_project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Backend Developer'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }