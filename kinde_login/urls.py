from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("other", views.other, name="other"),
    path("login", views.login, name="login"),
    path("callback", views.callback, name="callback"),
    path("logout", views.logout, name="logout"),
    path("register", views.register, name="register"),
]