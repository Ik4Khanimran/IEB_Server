# urls.py (inside the "Api" app)
from django.urls import path
from .views import LoginView, UserTable, CreateUserTable

app_name = 'User'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('usertable/', UserTable.as_view(), name='usertable'),
    path('createusertable/', CreateUserTable.as_view(), name='createusertable'),
]
