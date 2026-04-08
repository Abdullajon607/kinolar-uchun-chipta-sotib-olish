from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    # ========== BOSH SAHIFA ==========
    path('', views.home, name='home'),
    
    # ========== AUTENTIFIKATSIYA ==========
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== FILMLAR VA SEANSLAR ==========
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('select-seats/<int:showtime_id>/', views.select_seats, name='select_seats'),
    path('search/', views.search, name='search'),
    
    # ========== BRONIYA VA TO'LOV ==========
    path('save-seats/<int:showtime_id>/', views.save_selected_seats, name='save_seats'),
    path('checkout/<int:showtime_id>/', views.checkout, name='checkout'),
    path('process-payment/<int:showtime_id>/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='success'),
    
    # ========== CHIPTALAR ==========
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    
    # ========== TO'DO LIST ==========
    path('todo/', views.todo_list, name='todo_list'),
    
    # ========== API ENDPOINTS ==========
    path('api/todos/sync/', views.sync_todos, name='sync_todos'),
    path('api/movies/', views.get_movies_api, name='api_movies'),
    path('api/showtimes/<int:movie_id>/', views.get_showtimes_api, name='api_showtimes'),
]