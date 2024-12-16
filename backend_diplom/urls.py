"""
URL configuration for backend_diplom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, re_path
from mycloud import views
from mycloud.views import UserPostList, FileAPIUpdate, FileDownloadView, FileAPIDestroy, \
    UserListView, UserFileListView, UserDetailView , UserRegistrationView , index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/admin/users/', UserListView.as_view(), name='user-list'),
    path('api/v1/admin/users/<int:user_id>/files/', UserFileListView.as_view(), name='user-file-list'),
    path('api/v1/admin/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('api/v1/filelist/', UserPostList.as_view()),
    path('api/v1/download/<str:hash>/', FileDownloadView.as_view()), 
    path('api/v1/filelist/<int:pk>/', FileAPIUpdate.as_view()),
    path('api/v1/filedelete/<int:pk>/', FileAPIDestroy.as_view()), 
    path('api/v1/filelist/1', FileDownloadView.as_view()), 
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/register/', UserRegistrationView.as_view(), name='user-register'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    #TODO Все настройки для files static
    re_path(r'^.*$', views.index, name='index'),
]
