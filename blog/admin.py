from django.contrib import admin

from .models import DiaryPage


@admin.register(DiaryPage)
class DiaryPageAdmin(admin.ModelAdmin):
    list_display = ('written_date', 'search_date', 'page', 'created_at')
    search_fields = ('written_date', 'search_date', 'page')
    list_filter = ('written_date', 'search_date')
    ordering = ('-written_date', '-created_at')
