import os

from django.db import models
from rest_framework.exceptions import ValidationError

from products.models import SubCategory


class Product(models.Model):
    slug = models.SlugField(max_length=int(os.getenv('PRODUCT_SLUG_MAX_LEN')),
                            unique=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    name = models.CharField(max_length=int(os.getenv('PRODUCT_NAME_MAX_LEN')), )
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(null=False, blank=False)
    size_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk and self.product.product_images.count() > 3:
            raise ValidationError('Product should have not more than 3 images')
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('size_order',)
        constraints = [
            models.UniqueConstraint(fields=('product', 'size_order'),
                                    name='product_images_size_order_constraint')
        ]
