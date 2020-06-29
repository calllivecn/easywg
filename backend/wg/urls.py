#!/usr/bin/env python3
# coding=utf-8
# date 2020-06-19 09:22:27
# author calllivecn <c-all@qq.com>


from django.urls import path

from wg.authuser import Auth, Login

urlpatterns = [
    path("login/", Login.as_view()),
    path("logout/", Login.as_view()),
    path("auth/", Auth.as_view()),
]
