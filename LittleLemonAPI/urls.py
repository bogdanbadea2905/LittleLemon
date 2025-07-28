from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('reservations/', views.reservations, name="reservations"),
    path('bookings/', views.bookings, name="bookings"),
    path('menu/', views.menu, name="menu"),
    path('menu/<int:pk>/', views.display_menu_item, name="menu_item"),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('menu-items/featured/', views.ItemOfTheDayView.as_view()),
    path('categories/', views.CategoriesView.as_view()),
    path('token-auth/', obtain_auth_token),
    path('groups/manager/users/', views.managers),
    path('groups/manager/users/<int:userId>/', views.remove_manager),
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>/', views.remove_delivery),
    path('cart/menu-items/', views.CartMenuItemsView.as_view()),
    path('orders/', views.OrderListCreateView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
    # path('manager-view', views.manager_view),

]