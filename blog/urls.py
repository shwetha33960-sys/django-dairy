from django.urls import path
from .views import delete_page, home, login_view, logout_view, side_page

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('delete/<int:pk>/', delete_page, name='delete_page'),
    path('page/', side_page, name='side_page'),
    path('', home, name='home'),
]
