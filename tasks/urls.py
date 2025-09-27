
from django.urls import path
from . import views
from .views_logout import logout_view

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/member/<int:user_id>/', views.member_detail, name='member_detail'),
    path('logout/', logout_view, name='logout'),
]
