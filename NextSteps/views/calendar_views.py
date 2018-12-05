from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import datetime

from NextSteps.decorators import subscription_active

from NextSteps.models import InsttUserPref, UserCalendar
from NextSteps.models import InstituteImpDates

from .common_views import *

@login_required
@subscription_active
def calendar(request):

    return render(request, 'NextSteps/calendar_fullCal.html')
        
        
def getUserInstts(request):
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    userCalendar = UserCalendar.objects.filter(User__in=userid).values(
        'id', 'Institute__instt_name', 'event', 'event_date', 'event_order', 'start_date', 'end_date', 
        'event_duration_days', 'remarks').distinct('Institute__instt_name', 'event')
    
    if userCalendar.exists():
        return JsonResponse(list(userCalendar), safe=False)
    else:
    
        insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')
        
        '''
        insttList = InstituteProgramImpDates.objects.filter(Institute_id__in=insttUserList).values(
            'id', 'Institute_id', 'Institute__instt_name', 'event', 'event_date', 'event_order', 'start_date', 'end_date', 
            'event_duration_days', 'remarks').distinct('Institute__instt_name', 'event')
        '''
        insttList = InstituteImpDates.objects.filter(Institute_id__in=insttUserList).values(
            'id', 'Institute_id', 'Institute__instt_name', 'event', 'start_date', 'end_date', 
            'remarks').distinct('Institute__instt_name', 'event')


    return JsonResponse(list(insttList), safe=False)     

def getInsttImpDates(request):
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')

    '''        
    insttList = InstituteProgramImpDates.objects.filter(Institute_id__in=insttUserList).values(
            'id', 'Institute_id', 'Institute__instt_name', 'event', 'event_date', 'event_order', 'start_date', 'end_date', 
            'event_duration_days', 'remarks').distinct('Institute__instt_name', 'event')
    '''
    
    insttList = InstituteImpDates.objects.filter(Institute_id__in=insttUserList).values(
        'id', 'Institute_id', 'Institute__instt_name', 'event', 'start_date', 'end_date', 
        'remarks').distinct('Institute__instt_name', 'event')


    return JsonResponse(list(insttList), safe=False)     


@login_required
@csrf_exempt
def save_user_events(request):

    if request.is_ajax():
        if request.method == 'POST':

            # Get data from the request.
            json_data = json.loads(request.body.decode("utf-8"))

            # Get the user object for the logged in user
            usr = get_object_or_404(User, username=request.user)

            # delete the existing data
            UserCalendar.objects.filter(User=usr).delete()
            
            pass_fail = 'PASS'
            msg = 'SUCCESS'
                        
            for i in json_data:
                start = i.get("start", "")
                end = i.get("end", "")
                
                instt_name = i.get("instt_name", "")
                event = i.get("title", "")
                start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
                end_date = None
                if end != ('' or None):
                    end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
                id = i.get("id", "")
                instt_id = i.get("instt_id", "")
                remarks = i.get("remarks", "")

             
                try: 
                    # save the data
                    userCal = UserCalendar(id = id, User = usr, Institute_id = instt_id, 
                                event = event, event_date = start_date, start_date = start_date, 
                                end_date = end_date, remarks = remarks) 
                    userCal.save()

                except IntegrityError as e:
                    pass_fail = 'FAIL'
                    
                except Error as e:
                    pass_fail = 'FAIL'

    return HttpResponse(pass_fail)


@login_required
@subscription_active
def toDoList(request):

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    userCalendar = UserCalendar.objects.filter(User__in=userid).values(
        'id', 'Institute__instt_name', 'event', 'event_date', 'event_order', 'start_date', 'end_date', 
        'event_duration_days', 'remarks').distinct('Institute__instt_name', 'event')

    if userCalendar.exists():
        event_list = userCalendar
    else:
    
        insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')
        
        event_list = InstituteImpDates.objects.filter(Institute_id__in=insttUserList).values(
            'id', 'Institute_id', 'Institute__instt_name', 'event', 'start_date', 'end_date', 'remarks'
                ).distinct('Institute__instt_name', 'event')

    return render(request, 'NextSteps/to_do_list.html', {'event_list':event_list})



@login_required
@csrf_exempt
def delCalendarEventsByIDs(request):
    
    ids = request.POST.getlist("IDsToDelete[]",[])

    status = ''
    
    if not ids:
        status = '01'
        return JsonResponse({"status":status})

    for i in ids:
        delRec = UserCalendar.objects.filter(id = Decimal(i)).delete()
        if not delRec:
            status = "02"
            return JsonResponse( {"status":status} )
        
         
    status = "00" #Success
        
    return JsonResponse( {"status":status} )
    
    