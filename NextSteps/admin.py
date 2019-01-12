from django.contrib import admin
from .models import Institute, Program, InsttUserPref, ProgramUserPref, ContactForm
from .models import PromotionCode, UserAccount, UserProfile, JEEMAINdates, Partner, Partner_promo


admin.site.register(Institute)
admin.site.register(Program)
admin.site.register(InsttUserPref)
admin.site.register(ProgramUserPref)
admin.site.register(ContactForm)
admin.site.register(PromotionCode)
admin.site.register(UserAccount)
admin.site.register(UserProfile)
admin.site.register(JEEMAINdates)
admin.site.register(Partner)
admin.site.register(Partner_promo)