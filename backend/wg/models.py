from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class Users(models.Model):
#    username = models.CharField(max_length=64, primary_key=True, unique=True)
#    salt = models.CharField(max_length=32)
#    password = models.CharFireld(max_length=64)
#    changedate = models.DateField(auto_now=True)
#    registrydate = models.DateField(auto_now_add=True)


class ServerWg(models.Model):
    ifname = models.CharField(max_length=64, unique=True)
    ip = models.CharField(max_length=64)
    privatekey = models.CharField(max_length=64)
    publickey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    persistentkeepalive = models.IntegerField(default=25)

    boot = models.BooleanField(default=True)

    comment = models.TextField(max_length=128, blank=False, null=False)

class ClientWg(models.Model):
    server = models.ForeignKey(ServerWg, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=64)
    ifname = models.CharField(max_length=64, unique=True)
    privatekey = models.CharField(max_length=64)
    publickey = models.CharField(max_length=64)
    presharedkey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    persistentkeepalive = models.IntegerField(default=25)

    allowedips_s = models.TextField(max_length=4096)
    allowedips_c = models.TextField(max_length=4096)

    comment = models.TextField(max_length=128, blank=False, null=False)
