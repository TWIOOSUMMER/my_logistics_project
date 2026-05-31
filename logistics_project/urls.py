from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/logistics/', permanent=False), name='root'),
    path('admin/', admin.site.urls),
    path('logistics/', include('logistics.urls')),
]
