import os

from django.db import models



class Category(models.Model):
    name = models.CharField(max_length=int(os.getenv('CATEGORY_NAME_MAX_LEN')),
                            unique=True)
    slug = models.SlugField(max_length=int(os.getenv('CATEGORY_SLUG_MAX_LEN')),
                            unique=True)
    image = models.ImageField(null=False, blank=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
