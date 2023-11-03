from django.contrib import admin
from .models import Currency, History

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["abbr", "rate", "get_history"]

class HistoryAdmin(admin.ModelAdmin):
    list_display = ["currency", "date", "open", "high", "low", "close", "volume", "dividends", "stock_splits"]

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(History, HistoryAdmin)