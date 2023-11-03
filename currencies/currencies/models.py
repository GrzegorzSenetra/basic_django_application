from django.db import models
from django.contrib import admin
from django.utils.html import format_html
import json

class Currency(models.Model):
    abbr   = models.CharField(max_length=10)
    rate   = models.FloatField()
    
    def __str__(self):
        return self.abbr
    
    def save(self, *args, **kwargs):
        self.rate = round(self.rate, 4)
        super(Currency, self).save(*args, **kwargs)
    
    @admin.display(ordering="date")
    def get_history(self):
        return format_html(
            '<a href="/admin/currencies/history/?currency__id__exact={}">History</a>',
            self.id
        )
    
class History(models.Model):
    currency     = models.ForeignKey(Currency, on_delete=models.CASCADE)
    date         = models.DateField()
    open         = models.FloatField()
    high         = models.FloatField()
    low          = models.FloatField()
    close        = models.FloatField()
    volume       = models.IntegerField()
    dividends    = models.FloatField(default=0)
    stock_splits = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.open  = round(self.open,   4)
        self.high  = round(self.high,   4)
        self.low   = round(self.low,    4)
        self.close = round(self.close,  4)
        super(History, self).save(*args, **kwargs)