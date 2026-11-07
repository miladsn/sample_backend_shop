from django.db import models
from django.utils.text import slugify


class ProductStatus(models.TextChoices):
    DRAFT = 'draft', 'پیش‌نویس'
    PUBLISHED = 'published', 'منتشر شده'
    OUT_OF_STOCK = 'out_of_stock', 'ناموجود'
    ARCHIVED = 'archived', 'آرشیو شده'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان محصول')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, verbose_name='نامک (Slug)')
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='کد شناسه کالا (SKU)')
    categories = models.ManyToManyField('shop.Category', related_name='products', blank=True, verbose_name='دسته‌بندی‌ها')
    tags = models.ManyToManyField('shop.Tag', related_name='products', blank=True, verbose_name='برچسب‌ها')
    featured_image = models.ForeignKey('media_files.File', on_delete=models.SET_NULL, null=True, blank=True, related_name='product_featured_images', verbose_name='تصویر شاخص')
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='قیمت اصلی (تومان)')
    sale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت با تخفیف (تومان)')
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')
    available_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی قابل فروش"
    )

    short_description = models.TextField(max_length=500, blank=True, verbose_name='توضیحات کوتاه')
    description = models.TextField(blank=True, verbose_name='توضیحات کامل')
    status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.DRAFT, verbose_name='وضعیت محصول')
    is_featured = models.BooleanField(default=False, verbose_name='محصول ویژه')
    meta_title = models.CharField(max_length=255, blank=True, verbose_name='عنوان سئو (Meta Title)')
    meta_description = models.TextField(blank=True, verbose_name='توضیحات سئو (Meta Description)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        db_table = 'shop_products'
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return self.sale_price if self.sale_price and self.sale_price < self.price else self.price




    @property
    def is_in_stock(self) -> bool:
        return self.available_stock > 0 and self.status == ProductStatus.PUBLISHED

    # @property
    # def is_in_stock(self):
    #     return self.stock > 0 and self.status == ProductStatus.PUBLISHED

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images', verbose_name='محصول')
    file = models.ForeignKey('media_files.File', on_delete=models.CASCADE, related_name='product_gallery_items', verbose_name='فایل تصویر')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_product_images'
        ordering = ['display_order', 'id']

    def __str__(self):
        return f'Image for {self.product.title} (#{self.id})'
