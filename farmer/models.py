from django.db import models

# Create your models here.

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    mobile = models.CharField(max_length=15)
    village = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username