from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        role = str(user.role).lower()
        if role == 'admin' or user.is_superuser:
            return reverse_lazy('admin:index')
        elif role == 'manager':
            return reverse_lazy('project_list')
        else:
            return reverse_lazy('dashboard')
def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                LoginView(request, user) 
                return redirect('dashboard')
        else:
            form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})