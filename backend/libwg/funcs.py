
from django.http import JsonResponse

def json(j):
    return JsonResponse(j, json_dumps_params={"ensure_ascii": False, "indent": 4})

def resok(msg="successful"):
    return json({"code": 0, "msg": msg})

def reserr(msg, code=-1):
    return json({"code": code, "msg": msg})