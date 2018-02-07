from django.contrib import admin
from .models import Institute, Country, Discipline, Level, Program
# Register your models here.
admin.site.register(Institute)
admin.site.register(Country)
admin.site.register(Discipline)
admin.site.register(Level)
admin.site.register(Program)