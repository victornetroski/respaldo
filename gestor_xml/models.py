from django.db import models
from django.contrib.auth.models import User

class XMLFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)