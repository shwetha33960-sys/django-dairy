from django.db import models


class DiaryPage(models.Model):
    search_date = models.DateField(blank=True, null=True)
    written_date = models.DateField(blank=True, null=True)
    page = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-written_date', '-created_at']

    def __str__(self):
        return f"{self.written_date or self.search_date or 'No date'} - {self.page[:30]}"
