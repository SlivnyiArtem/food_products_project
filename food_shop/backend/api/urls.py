from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from api.views import CartViewSet, CategoriesViewSet, ProductsViewSet

router = routers.DefaultRouter()

router.register(r'categories', CategoriesViewSet, basename='category')
router.register(r'products', ProductsViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='cart')


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
