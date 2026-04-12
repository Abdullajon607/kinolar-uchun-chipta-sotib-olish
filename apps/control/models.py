from django.db import models


class SiteSetting(models.Model):
    """Umumiy sozlamalar (REST va admin orqali boshqarish)."""

    key = models.SlugField(max_length=64, unique=True, verbose_name="Kalit")
    value = models.TextField(blank=True, verbose_name="Qiymat")
    description = models.CharField(max_length=255, blank=True, verbose_name="Izoh")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Sayt sozlamasi"
        verbose_name_plural = "Sayt sozlamalari"
        ordering = ["key"]

    def __str__(self):
        return self.key
