from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'Admin'
    MANAGER = 'Manager'
    DEVELOPER = 'Developer'

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'MANAGER'),
        (DEVELOPER, 'Developer'),
    )

    role = models. CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=DEVELOPER
    ) 
    email = models.EmailField(unique=True)

    def __str__(self):
       return f"{self.username} ({self.role})"
   

