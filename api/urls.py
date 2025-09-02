from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('search', views.SearchDataAPI.as_view(), name='search'),
    path('upload', views.UploadJsonAPI.as_view(), name='upload'),
    path('download/<int:pk>', views.DownloadJsonAPI.as_view(), name='download'),

]