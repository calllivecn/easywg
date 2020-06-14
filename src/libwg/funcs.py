
from django.http import JsonResponse

def json(j):
    return JsonResponse(j, json_dumps_params={"ensure": False, "indent": 4})

def resok(msg="successful"):
    return json({"code": 0, "msg": msg})

def reserr(code=-1, msg):
    return json({"code": code, "msg": msg})