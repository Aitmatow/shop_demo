from django.urls import path
from .views import IndexView, ProductView, ProductCreateView, BasketChangeView, BasketView, ProductUpdateView, \
    ProductDeleteView, OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderProductCreateView, \
    OrderProductUpdateView, OrderProductDeleteView, OrderDeliverView, OrderCancelView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('basket/change/', BasketChangeView.as_view(), name='basket_change'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('products/<int:pk>/update', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete', ProductDeleteView.as_view(), name='product_delete'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/create', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order_update'),
    path('orders/product/create/<int:pk>', OrderProductCreateView.as_view(),name='order_product_create'),
    path('orders/product/update/<int:pk>/<int:id>', OrderProductUpdateView.as_view(), name='order_product_update'),
    path('orders/product/delete/<int:pk>/<int:id>', OrderProductDeleteView.as_view(), name='order_product_delete'),
    path('orders/deliver/<int:pk>', OrderDeliverView.as_view(),name='order_deliver'),
    path('orders/cancel/<int:pk>', OrderCancelView.as_view(),name='order_cancel'),
]
