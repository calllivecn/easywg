# Create your views here.
#!/usr/bin/env python3
# coding=utf-8
# date 2020-06-08 10:05:02
# author calllivecn <c-all@qq.com>


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View


class Jquery(View):

    template = "jquery/jquery.html"

    def get(self, request):
        return render(request, self.template, {"context": "内容"})


