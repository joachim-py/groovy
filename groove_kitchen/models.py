from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    validation_code = models.CharField(max_length=10, null=True, blank=True)
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"
    
