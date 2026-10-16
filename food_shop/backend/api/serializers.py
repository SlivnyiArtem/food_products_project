from rest_framework import serializers

from products.models import Product, Category, SubCategory
from products.models.product import ProductImage
from products.models.user_mtm import UserCartProduct

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('image', 'size_order')

class ProductReadSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)
    category = serializers.CharField(source='subcategory.category.name', read_only=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('name', 'slug', 'subcategory', 'category', 'price', 'images')
        read_only_fields = fields

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('name','slug','image')

class CategoryReadSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ('name', 'image', 'slug', 'subcategories')

class CardSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),
                                                    source='product')
    quantity = serializers.IntegerField(min_value=1, required=False, default=1)

    class Meta:
        model = UserCartProduct
        fields = ('id', 'product_id', 'quantity')

class CardReadSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.product.price * cart_item.quantity

    class Meta:
        model = UserCartProduct
        fields = ('product', 'quantity', 'total_price')
        read_only_fields = fields
