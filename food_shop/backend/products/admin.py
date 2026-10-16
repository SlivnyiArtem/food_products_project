from django.contrib import admin
from django.contrib.auth import get_user_model

from products.models import Category, SubCategory, Product
from products.models.product import ProductImage

User = get_user_model()

admin.site.register((Category, SubCategory,))

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
