from django.conf import settings
from django.db import models


class UserCartProduct(models.Model):
    customer = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='products_in_carts'
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('customer', 'product'), name='unique_product_purchase'
            ),
        ]

    def __str__(self):
        return self.product.name + ' ' + self.customer.username
