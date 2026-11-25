from django.urls import path
from . import views
from . import category_budgets as cb

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('budget/', views.set_budget, name='set_budget'),
    path('category-budgets/', cb.category_budgets, name='category_budgets'),
    path('category-budgets/<int:pk>/delete/', cb.category_budget_delete, name='category_budget_delete'),
]