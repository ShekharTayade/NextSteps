from NextSteps.models import InstitutePrograms

from django import template

register = template.Library()
@register.inclusion_tag('NextSteps/instt_prog_group_lookup.html')

def instt_prog_group_lookup(request):
    
    progVals = request.GET.getlist('progValues', [])
    insttVals = request.GET.getlist('insttValues', [])
    
    progs = InstitutePrograms.objects.all().order_by ('Program__program_group').values(
		'Program__program_group', 'Program_id', 'Institute__instt_name')
    
    if progVals :
        progs = progs.filter(Program_id__in = progVals)
        
    if insttVals:
        progs = progs.filter(Institute_id__in = insttVals)

    return ({'progs':progs})    