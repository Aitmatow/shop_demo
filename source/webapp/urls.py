from django.urls import path
from .views import IndexView, ProductView, ProductCreateView, BasketChangeView, BasketView, ProductUpdateView, \
    ProductDeleteView, OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderProductCreateView, \
    OrderProductUpdateView, OrderProductDeleteView, OrderDeliverView, OrderCancelView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductView.as_view(), name='product_detail'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    path('basket/change/', BasketChangeView.as_view(), name='basket_change'),
    path('basket/', BasketView.as_view(), name='basket'),

    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('order/<int:pk>/deliver/', OrderDeliverView.as_view(), name='order_deliver'),
    path('order/<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),

    path('order/<int:pk>/add-product/', OrderProductCreateView.as_view(), name='order_add_product'),
    path('order-product/<int:pk>/update/', OrderProductUpdateView.as_view(), name='order_product_update'),
    path('order-product/<int:pk>/delete/', OrderProductDeleteView.as_view(), name='order_product_delete'),
]
