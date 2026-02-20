from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        # Role ko lowercase mein convert karein taki spelling ka panga na ho
        role = str(user.role).lower()
        
        if role == 'admin' or user.is_superuser:
            return reverse_lazy('admin:index')
        elif role == 'manager':
            return reverse_lazy('project_list')
        else:
            return reverse_lazy('dashboard')