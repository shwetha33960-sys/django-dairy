from django.conf import settings
from django.db import models


class DiaryPage(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diary_pages',
        null=True,
        blank=True,
    )
    search_date = models.DateField(blank=True, null=True)
    written_date = models.DateField(blank=True, null=True)
    page = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-written_date', '-created_at']

    def __str__(self):
        return f"{self.written_date or self.search_date or 'No date'} - {self.page[:30]}"


class TodoItem(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todo_items',
    )
    title = models.CharField(max_length=300)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completed', '-created_at']

    def __str__(self):
        status = '✓' if self.completed else '○'
        return f"{status} {self.title[:50]}"

