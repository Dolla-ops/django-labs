from django.urls import path
from . import views

urlpatterns = [
    # ── Лаба 5: Головна ──────────────────────────────────────────────────────
    path('', views.home, name='home'),

    # ── Лаба 5/6: Жанри і фільми ─────────────────────────────────────────────
    path('genre/<slug:slug>/', views.genre_detail, name='genre_detail'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),

    # ── Лаба 7: Кошик ────────────────────────────────────────────────────────
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:session_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:ticket_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),

    # ── Лаба 8: Авторизація ───────────────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]
