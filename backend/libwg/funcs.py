
from django.http import JsonResponse

def json(j):
    return JsonResponse(j, json_dumps_params={"ensure_ascii": False, "indent": 4})

def res(data):
    j = []
    j["code"] = 0
    j["msg"] ="ok"
    j["data"] = data
    return json(j)

def resok(msg="ok"):
    return json({"code": 0, "msg": msg})

def reserr(msg, code=-1):
    return json({"code": code, "msg": msg})