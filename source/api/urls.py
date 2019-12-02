from django.urls import path

from .views import product_list_view, product_list_view_v2, product_create_view, product_create_view_v2

app_name = 'api_v1'

urlpatterns = [
    path('products/', product_list_view, name='product_list'),
    path('products/v2/', product_list_view_v2, name='product_list_v2'),
    path('products/create/', product_create_view, name='product_create'),
    path('products/create/v2/', product_create_view_v2, name='product_create_v2')
]