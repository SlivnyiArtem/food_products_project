import os

from django.shortcuts import get_object_or_404
from products.models import Category, Product
from products.models.user_mtm import UserCartProduct
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.pagination import SimplePagination
from api.permissions import IsCartOwner
from api.serializers import (
    CardReadSerializer,
    CardSerializer,
    CategoryReadSerializer,
    ProductReadSerializer,
)


class CartViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = (IsCartOwner,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return CardReadSerializer
        return CardSerializer

    def get_queryset(self):
        return UserCartProduct.objects.filter(
            customer=self.request.user
        ).select_related('product')

    @action(
        detail=False,
        methods=('post',),
    )
    def add_shopping_cart(self, request):
        """Добавление товара в корзину."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        mtm_product, created = UserCartProduct.objects.get_or_create(
            customer=request.user,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            mtm_product.quantity += quantity
            mtm_product.save(update_fields=['quantity'])
            return Response(
                data=CardReadSerializer(mtm_product).data,
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            data=CardReadSerializer(mtm_product).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=('patch',),
        url_path='set_quantity',
    )
    def set_product_quantity(self, request):
        """Изменение количества продукта в корзине."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        cart_item = UserCartProduct.objects.filter(
            customer=request.user, product=product
        ).first()

        if not cart_item:
            return Response(
                {'detail': os.getenv('PRODUCT_NOT_FOUND_MESSAGE')},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not quantity > 0:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        cart_item.quantity = quantity
        cart_item.save(update_fields=['quantity'])
        return Response(
            data=CardReadSerializer(cart_item).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['delete'], url_path='remove')
    def delete_product_from_shopping_cart(self, request, pk):
        """Удаление количества продукта в корзине."""
        product = get_object_or_404(Product, pk=pk)

        del_cnt, _ = UserCartProduct.objects.filter(
            customer=request.user,
            product=product,
        ).delete()

        if del_cnt > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': os.getenv('PRODUCT_NOT_FOUND_MESSAGE')},
            status=status.HTTP_404_NOT_FOUND,
        )

    def list(self, request, *args, **kwargs):
        """Просмотр продуктов в корзине."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_price = sum(i.quantity * i.product.price for i in queryset)
        total_quantity = sum(i.quantity for i in queryset)
        return Response(
            {
                'items': serializer.data,
                'total_quantity': total_quantity,
                'total_price': total_price,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['delete'], url_path='clear_cart')
    def clear_cart(self, request):
        """Очистка корзины."""
        deleted_cnt, _ = self.get_queryset().delete()
        return Response(
            {'deleted_cnt': deleted_cnt}, status=status.HTTP_204_NO_CONTENT
        )


class ProductsViewSet(ReadOnlyModelViewSet):
    pagination_class = SimplePagination
    permission_classes = (AllowAny,)
    serializer_class = ProductReadSerializer

    def get_queryset(self):
        return (
            Product.objects.select_related('subcategory__category')
            .prefetch_related('product_images')
            .order_by('id')
        )


class CategoriesViewSet(ReadOnlyModelViewSet):
    pagination_class = SimplePagination
    permission_classes = (AllowAny,)
    serializer_class = CategoryReadSerializer

    def get_queryset(self):
        return Category.objects.all().prefetch_related('subcategories')
