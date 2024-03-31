#!/usr/bin/env python3
# coding=utf-8
# date 2020-06-19 09:22:27
# author calllivecn <calllivecn@outlook.com>

from django.views.decorators.csrf import csrf_exempt
from django.urls import path

from wg.login import Logined, Login, Logout, Chpassword

urlpatterns = [
    path("logined/", Logined.as_view()),
    path("login/", csrf_exempt(Login.as_view())),
    path("logout/", Logout.as_view()),
    path("chpassword/", Chpassword.as_view()),
]
