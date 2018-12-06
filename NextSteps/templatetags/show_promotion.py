from NextSteps.models import PromotionCode

from django import template
from datetime import datetime
import datetime


today = datetime.date.today()

register = template.Library()
@register.inclusion_tag('NextSteps/show_promo.html')
def promo_display(request):
	
	# Get promos from DB
	disp_promo = PromotionCode.objects.filter(end_date__gte = today, display_in_homepage = True).first()
	
	return ({'disp_promo':disp_promo})
