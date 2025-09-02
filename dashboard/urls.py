from django.urls import path

from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('data/<int:pk>', views.DataDetailView.as_view(), name='detail'),
    path('data/download/<int:pk>', views.DownloadData.as_view(), name='download'),
    path('add', views.AddDataView.as_view(), name='add_data'),
    path('login', views.UserLoginView.as_view(), name='user_login'),
    path('logout', views.LogoutView.as_view(), name='user_logout'),
]
