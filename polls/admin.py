from django.contrib import admin
from .models import Event,EventOption,ParticipateIn

admin.site.register(Event)
admin.site.register(EventOption)
admin.site.register(ParticipateIn)
# class EventAdmin(admin.ModelAdmin):
    # list_display = ['name','description','repeating_day','holding_date_from' , 'holding_date_to','ending_date']
