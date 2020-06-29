from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#class Users(models.Model):
#    username = models.CharField(max_length=64, primary_key=True, unique=True)
#    salt = models.CharField(max_length=32)
#    password = models.CharFireld(max_length=64)
#    changedate = models.DateField(auto_now=True)
#    registrydate = models.DateField(auto_now_add=True)


class ServerWg(models.Model):
    ifname = models.CharField(max_length=32, unique=True)
    privatekey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    allowedips = models.TextField(null=True)


class ClientWg(models.Model):
    server = models.ForeignKey(ServerWg, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ifname = models.CharField(max_length=32, unique=True)
    privatekey = models.CharField(max_length=64)
    presharedkey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    allowedips = models.TextField()
