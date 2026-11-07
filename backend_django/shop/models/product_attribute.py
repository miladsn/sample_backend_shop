from django.db import models

from shop.models import Product


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name="محصول"
    )
    key = models.CharField(max_length=150, verbose_name="عنوان مشخصه")
    value = models.CharField(max_length=255, verbose_name="مقدار")
    display_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات فنی محصول"

    def __str__(self):
        return f"{self.key}: {self.value}"
