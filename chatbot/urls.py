from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name= 'index'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('adminpage/', views.adminpage, name='adminpage'),
    path('upload/', views.upload, name='upload'),
    path('employee/', views.employee, name='employee'),
    path('logout/', views.logout_user, name='logout_user'),
    path('getResponse/', views.getResponse, name='getResponse'),
    path('getChatHistory', views.getChatHistory, name='getChatHistory'),
    path('add-holiday/', views.add_holiday, name='add_holiday'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

