"""Persistent journal structure and Django field constraints."""

from django.conf import settings
from django.db import models


class Topic(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField("Tên chủ đề", max_length=200)
    date_added = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        ordering = ["-date_added", "-pk"]
        indexes = [models.Index(fields=["owner", "-date_added"])]
        verbose_name = "Chủ đề"
        verbose_name_plural = "Chủ đề"

    def __str__(self) -> str:
        return self.text


class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="entries")
    text = models.TextField("Nội dung")
    date_added = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Lần chỉnh sửa", auto_now=True)

    class Meta:
        ordering = ["-date_added", "-pk"]
        indexes = [models.Index(fields=["topic", "-date_added"])]
        verbose_name = "Ghi chép"
        verbose_name_plural = "Ghi chép"

    def __str__(self) -> str:
        return self.text[:80]
