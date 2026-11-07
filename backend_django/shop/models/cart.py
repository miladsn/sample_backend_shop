from decimal import Decimal
from django.conf import settings
from django.db import models
from shop.models.product import Product
from shop.models.option import ProductOptionItem


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
        verbose_name="کاربر"
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="کلید نشست"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        db_table = 'shop_carts'
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"Cart #{self.id} - {'User: ' + str(self.user) if self.user else 'Guest: ' + str(self.session_key)}"

    @property
    def total_items_count(self) -> int:
        """تعداد کل آیتم‌ها در سبد خرید"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self) -> Decimal:
        """جمع کل مبلغ سبد خرید"""
        return sum((item.unit_price * item.quantity) for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سبد خرید"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="محصول"
    )
    # Selected variant (color, size, or the final leaf of the options tree)
    option_item = models.ForeignKey(
        ProductOptionItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        verbose_name="تنوع / واریانت"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        db_table = 'shop_cart_items'
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        # A product with a specific variant should not appear multiple times in the cart; instead, its quantity should be increased.
        unique_together = ('cart', 'product', 'option_item')

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"

    @property
    def unit_price(self) -> Decimal:
        """Unit price calculation: Priority is given to the variant price; otherwise, the product's own price is used."""
        if self.option_item:
            if self.option_item.special_price is not None:
                return self.option_item.special_price
            if self.option_item.price is not None:
                return self.option_item.price
        return self.product.final_price

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity
