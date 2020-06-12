from django.db import models

# Create your models here.


class ServerWg(models.Model):
    ifname = models.CharField(max_length=32, unique=True)
    privatekey = models.CharField(max_length=64)
    presharedkey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    allowedips = models.TextField(null=True)


class ClientWg(models.Model):
    server = models.ForeignKey(ServerWg, on_delete=models.CASCADE)
    user = alskdfjief()
    ifname = models.CharField(max_length=32, unique=True)
    privatekey = models.CharField(max_length=64)
    presharedkey = models.CharField(max_length=64)
    listenport = models.IntegerField(blank=True, null=True)
    allowedips = models.TextField()