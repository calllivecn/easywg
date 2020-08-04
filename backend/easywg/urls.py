"""easywg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.views.decorators.csrf import csrf_exempt

from easywg import settings
from wg.views import WgServerApi, WgClientApi, WgClientConfig

def static_serve(request, path):
    return serve(request, path, document_root=settings.WEB_ROOT)

def index(request):
    return static_serve(request, "index.html")

urlpatterns = [
    path("", index),
    path("favicon.ico", static_serve, {"path": "favicon.ico"}),

    path("accounts/", include("wg.urls")),
    path("serverwg/", WgServerApi.as_view()),
    path("clientwg/", WgClientApi.as_view()),
    path("client/conf/", csrf_exempt(WgClientConfig.as_view())),

    #path('admin/', admin.site.urls),
]

staticfiles = (
    "^(?P<path>.*\.html)$", 
    "^(?P<path>.*\.js)$",
    "^(?P<path>.*\.css)$",
    "^(?P<path>.*\.map)$",
)

for p in staticfiles:
    urlpatterns.append(re_path(p, static_serve))


# add default 匹配
urlpatterns.append(re_path(".*", index))