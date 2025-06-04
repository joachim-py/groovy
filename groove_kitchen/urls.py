from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="home"),
    path('about-us/', views.about_us, name="about_us"),
    path('login/', views.login_view, name="login_view"),
    path('logout/', views.logout_view, name="logout_view"),
    path('registration/', views.registration, name="registration"),
    path('password-form/', views.password_form, name='password_form'),
    path('password-done/', views.password_done, name='password_done'),
    path('password/<int:uidb64>/', views.password_confirm, name='password_confirm'),
    path('password/complete/', views.password_complete, name='password_complete'),
]
