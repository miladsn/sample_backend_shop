from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان برچسب')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True, verbose_name='اسلاگ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب‌ها'
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
