import os

from django.db import models

from .category import Category


class SubCategory(models.Model):
    name = models.CharField(
        max_length=int(os.getenv("SUB_CATEGORY_NAME_MAX_LEN")),
    )
    slug = models.CharField(
        max_length=int(os.getenv("SUB_CATEGORY_SLUG_MAX_LEN")),
    )
    image = models.ImageField(null=False, blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
