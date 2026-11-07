from django.db import models


class ProductAlbum(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'تصویر'
        VIDEO = 'video', 'ویدیو'

    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='album_items', verbose_name='محصول')
    file = models.ForeignKey('media_files.File', on_delete=models.CASCADE, related_name='product_albums', verbose_name='فایل مدیا')
    media_type = models.CharField(max_length=10, choices=MediaType.choices, default=MediaType.IMAGE, verbose_name='نوع رسانه')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        db_table = 'shop_product_albums'
        verbose_name = 'آلبوم محصول'
        verbose_name_plural = 'آلبوم‌های محصول'
        ordering = ['display_order', 'id']

    def __str__(self):
        return f'{self.product.title} - {self.file.original_name}'
