import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    is_admin= models.BooleanField('Is admin', default=False)
    
    is_employee = models.BooleanField('Is employee', default=False)

class Upload(models.Model):
   
    collection_name = models.CharField(max_length=100, default='collection')
    file_name = models.FileField(upload_to = "./document" , null=True, unique=True)
    title = models.CharField(max_length=100, default='collection_title')
    description = models.CharField(max_length=100, default='collection_description')

class UserRedisHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redis_histories')
    redis_key = models.CharField(max_length=255, default=str(uuid.uuid4()), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Holiday(models.Model):
    name = models.CharField(max_length=100)  
    date = models.DateField()  