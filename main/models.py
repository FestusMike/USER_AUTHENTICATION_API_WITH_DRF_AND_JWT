from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False, unique= True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    username= models.CharField(max_length=100, null=True, blank=True, unique=True)
    avatar = models.ImageField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'UserDB'

    def __str__(self):
        return self.username

class Project(models.Model):
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique = True)
    project_owner = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ProjectDB'
    
    def __str__(self):
        return self.title
    
