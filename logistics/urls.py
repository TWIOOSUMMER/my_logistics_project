from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('goods/add/', views.goods_add, name='goods_add'),
    path('goods/edit/<int:goods_id>/', views.goods_edit, name='goods_edit'),
    path('goods/delete/<int:goods_id>/', views.goods_delete, name='goods_delete'),
    path('goods/export/', views.goods_export, name='goods_export'),
    path('goods/import/', views.goods_import, name='goods_import'),
    path('category/add/', views.category_add, name='category_add'),
    path('order/add/', views.order_add, name='order_add'),
    path('order/edit/<int:order_id>/', views.order_edit, name='order_edit'),
    path('order/delete/<int:order_id>/', views.order_delete, name='order_delete'),
    path('order/status/<int:order_id>/', views.order_status_change, name='order_status_change'),
    path('order/batch/', views.order_batch_status, name='order_batch_status'),
    path('order/export/', views.order_export, name='order_export'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/print/<int:order_id>/', views.order_print, name='order_print'),
]
