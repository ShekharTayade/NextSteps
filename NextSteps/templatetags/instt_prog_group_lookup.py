'''
from NextSteps.models import InstitutePrograms

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django import template

register = template.Library()
@register.inclusion_tag('NextSteps/instt_prog_group_lookup.html')

def instt_prog_group_lookup(request):
    
	progVals = request.GET.getlist('progValues', [])
	insttVals = request.GET.getlist('insttValues', [])
    
	progs_group = InstitutePrograms.objects.all().order_by ('Program__program_group').values(
		'Program__program_group', 'Program_id', 'Institute__instt_name')
	
	if progVals :
		progs_group = progs_group.filter(Program_id__in = progVals)
        
	if insttVals:
		progs_group = progs_group.filter(Institute_id__in = insttVals)
	
	paginator = Paginator(progs_group, 10000) 
	page = request.GET.get('page')
	progs = paginator.get_page(page)
	
	return ({'progs':progs})
'''