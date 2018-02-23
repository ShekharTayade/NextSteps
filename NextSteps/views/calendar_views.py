from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error
from django.db.models import Q

from datetime import datetime

from NextSteps.decorators import subscription_active

from NextSteps.models import InsttUserPref
from NextSteps.models import InstituteProgramImpDates

from .common_views import *

@login_required
@subscription_active
def calendar(request):

    return render(request, 'NextSteps/calendar_fullCal.html')
        
        
def getUserInstts(request):
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')
    
    insttList = InstituteProgramImpDates.objects.filter(Institute_id__in=insttUserList).values(
        'id', 'Institute__abbreviation', 'event', 'event_date', 'event_order', 'start_date', 'end_date', 
        'event_duration_days', 'remarks').order_by('Institute__instt_name', 'event_date')


    return JsonResponse(list(insttList), safe=False)     
