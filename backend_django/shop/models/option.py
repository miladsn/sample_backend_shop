from django.db import models
from django.utils.text import slugify


class ProductOptionGroup(models.Model):
    class GroupType(models.TextChoices):
        COLOR = 'color', 'رنگ'
        SIZE = 'size', 'سایز'
        TEXT = 'text', 'متن'
        IMAGE = 'image', 'تصویر'

    title = models.CharField(max_length=100, verbose_name='عنوان گروه')
    slug = models.SlugField(max_length=120, unique=True, verbose_name='نامک')
    group_type = models.CharField(max_length=10, choices=GroupType.choices, default=GroupType.TEXT, verbose_name='نوع نمایش در فرانت‌اند')

    class Meta:
        db_table = 'shop_product_option_groups'
        verbose_name = 'گروه ویژگی محصول'
        verbose_name_plural = 'گروه‌های ویژگی محصول'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductOptionValue(models.Model):
    group = models.ForeignKey(ProductOptionGroup, on_delete=models.CASCADE, related_name='values', verbose_name='گروه مربوطه')
    title = models.CharField(max_length=100, verbose_name='عنوان مقدار')
    slug = models.SlugField(max_length=120, blank=True, verbose_name='نامک')
    value_data = models.CharField(max_length=255, verbose_name='مقدار فنی')

    class Meta:
        db_table = 'shop_product_option_values'
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی'

    def __str__(self):
        return f'{self.group.title} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductOptionItem(models.Model):
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='option_items', verbose_name='محصول')
    option_value = models.ForeignKey(ProductOptionValue, on_delete=models.CASCADE, verbose_name='مقدار ویژگی')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name='والد')
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت اختصاصی')
    special_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت ویژه')
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    available_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='موجودی قابل فروش'
    )
    class Meta:
        db_table = 'shop_product_option_items'
        verbose_name = 'آیتم آپشن محصول'
        verbose_name_plural = 'آیتم‌های آپشن محصول'

    def __str__(self):
        return f'{self.product.title} - {self.option_value.title}'
