from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error
from django.db.models import Q
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from random import randrange

from datetime import datetime, timedelta, date

from NextSteps.decorators import subscription_active

from NextSteps.forms import SignUpForm, UserAppDetailsForm
from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import Country, Discipline, Level, Program, InstitutePrograms
from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref
from NextSteps.models import ProgramUserPref, InsttUserPref, InstituteProgramSeats
from NextSteps.models import InstituteEntranceExam, InstituteProgramImpDates
from NextSteps.models import StudentCategory, StudentCategoryUserPref, InstituteAdmRoutes
from NextSteps.models import UserAppDetails, UserProfile
from NextSteps.models import Subjects, UserSubjectSchedule, UserStudySchedule
from NextSteps.models import StudyHours, UserDaySchedule

from .common_views import *
from .pdf_views import *
from .calendar_views import *
import json

from NextSteps.forms import UserSubjectScheduleForm

from django.forms import modelformset_factory
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.dates import MONTHS
from django.db.models import Min, Max, Sum
from django.db.models.functions import Extract, Coalesce
from decimal import Decimal

from _pytest.logging import get_actual_log_level

#from idlelib.colorizer import prog
#from reportlab.pdfgen import canvas
#from reportlab.lib.units import inch
#from reportlab.lib.pagesizes import letter, A4

@login_required
@subscription_active
def userPref(request):
    
    # Get all records to be displayed 
    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    programList = Program.objects.all().order_by('description')
    levelList = Level.objects.all()
    insttProgList = InstitutePrograms.objects.filter(Country__in=countryList, 
                Discipline__in=disciplineList, Level__in=levelList,
                Program__in=programList ).values('Institute__instt_name',
                'Program_id')
    insttList = insttProgList.distinct().values('Institute__instt_name').order_by('Institute__instt_name')
    stuCategoryList = StudentCategory.objects.values('description').order_by('description').distinct()
    
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    # Get the records already saved by user earlier and pass those to the template
    countryUserList = CountryUserPref.objects.filter(User__in=userid).values('Country__country_name')
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid).values('Discipline__description')
    programUserList = ProgramUserPref.objects.filter(User__in=userid).values('Program__description').order_by('Program__description')
    levelUserList = LevelUserPref.objects.filter(User__in=userid).values('Level__level_name')
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_name').order_by('Institute__instt_name').distinct()
    
    stuUserCat = StudentCategoryUserPref.objects.filter(User__in=userid).values('StudentCategory__description').order_by('StudentCategory__description').distinct()

    return render(request, 'NextSteps/pref_setViewPrefs.html', {
        'countryList': countryList, 'disciplineList':disciplineList, 
        'levelList':levelList, 'programList':programList,
        'insttProgList':insttProgList, 'insttList':insttList,
        'countryUserList':countryUserList, 'disciplineUserList':disciplineUserList,
        'programUserList':programUserList, 'stuUserCat':stuUserCat, 'stuCategoryList':stuCategoryList,
        'levelUserList':levelUserList, 'insttUserList':insttUserList })


def getInsttsForProgs(request):
    countryVals = request.GET.getlist('cntList', [])
    disciplineVals = request.GET.getlist('discList', [])
    levelVals = request.GET.getlist('lvlList', [])
    programVals  = request.GET.getlist('progList[]', [])


    # There might be white spaces in the array items. Let's remove those
    cntList = []
    for c in countryVals:
        c = c.strip()
        cntList.append(c)        

    discList = []
    for d in disciplineVals:
        d = d.strip()
        discList.append(d)        

    lvlList = []
    for l in levelVals:
        l = l.strip()
        lvlList.append(l)        

    progList = []
    for p in programVals:
        p = p.strip()
        progList.append(p)        


    # Get country, discipline and level Codes
    countryCodes = Country.objects.filter(country_name__in = cntList).values(
            'country_code')
    disciplineCodes = Discipline.objects.filter(description__in = discList).values(
            'discipline_code')
    levelCodes = Level.objects.filter(level_name__in = lvlList).values(
            'level_code')
    
    if progList:
        insttList = InstitutePrograms.objects.filter(Country__in=countryCodes, 
                    Discipline__in=disciplineCodes, Level__in=levelCodes, 
                    Institute__jee_flag = "Y", Program_id__in=progList ).values(
                        'Institute__instt_name').distinct().order_by(
                        'Institute__instt_name')
    else:
        insttList = InstitutePrograms.objects.filter(Country__in = countryCodes, 
                    Discipline__in=disciplineCodes, Level__in=levelCodes,
                    Institute__jee_flag = "Y").values(
                        'Institute__instt_name').distinct().order_by('Institute__instt_name')
        
    return JsonResponse(list(insttList), safe=False)    
    

def getProgsForInstts(request):
    countryVals = request.GET.getlist('cntList', [])
    disciplineVals = request.GET.getlist('discList', [])
    levelVals = request.GET.getlist('lvlList', [])
    insttNmVals  = request.GET.getlist('insttList[]', [])

    # There might be white spaces in the array items. Let's remove those
    cntList = []
    for c in countryVals:
        c = c.strip()
        cntList.append(c)        

    discList = []
    for d in disciplineVals:
        d = d.strip()
        discList.append(d)        

    lvlList = []
    for l in levelVals:
        l = l.strip()
        lvlList.append(l)        

    insttnmList = []
    for i in insttNmVals:
        i = i.strip()
        insttnmList.append(i)        


    # Get country, discipline and level Codes
    countryCodes = Country.objects.filter(country_name__in = cntList).values(
            'country_code')
    disciplineCodes = Discipline.objects.filter(description__in = discList).values(
            'discipline_code')
    levelCodes = Level.objects.filter(level_name__in = lvlList).values(
            'level_code')
    
    if insttnmList:
        progList = InstitutePrograms.objects.filter(Country__in=countryCodes, 
                    Discipline__in=disciplineCodes, Level__in=levelCodes,
                    Institute__instt_name__in=insttnmList).values(
                        'Program_id').distinct().order_by('Program_id')
    else:
        progList = InstitutePrograms.objects.filter(Country__in=countryCodes, 
                    Discipline__in=disciplineCodes, Level__in=levelCodes).values(
                        'Program_id').distinct().order_by('Program_id')
                        
    return JsonResponse(list(progList), safe=False)    


@login_required
@subscription_active
def userPrefConfirm(request):


    countryVals = request.GET.getlist('countryList', [])
    disciplineVals = request.GET.getlist('disciplineList', [])
    levelVals = request.GET.getlist('levelList', [])
    stuCatVals = request.GET.getlist('stuCategoryList', [])
    programVals  = request.GET.getlist('prefProgramsList', [])
    insttVals = request.GET.getlist('prefInstitutesList', [])

    # There might be white spaces in the array items. Let's remove those
    cntList = []
    for c in countryVals:
        c = c.strip()
        cntList.append(c)        

    discList = []
    for d in disciplineVals:
        d = d.strip()
        discList.append(d)        

    lvlList = []
    for l in levelVals:
        l = l.strip()
        lvlList.append(l)        

    stuCatList = []
    for s in stuCatVals:
        s = s.strip()
        stuCatList.append(s)        

    insttnmList = []
    for i in insttVals:
        i = i.strip()
        insttnmList.append(i)        

    progList = []
    for p in programVals:
        p = p.strip()
        progList.append(p)        

    
    """
    countryVals = request.GET.get('CountryValues', 'Blank').split(";")
    disciplineVals = request.GET.get('DisciplineValues', 'Blank').split(";")
    levelVals = request.GET.get('LevelValues', 'Blank').split(";")
    programVals = request.GET.get('ProgramValues', 'Blank').split(";")
    insttVals = request.GET.get('InsttValues', 'Blank').split(";")
    stuCatVals = request.GET.get('stuCatValues', 'Blank').split(";")
    """

    ############################################################################
    # Currently on "India" as country, "Engineering" as Discipline and 
    # "Undergraduation" as Level ae supported by NextSteps
    # This code to be removed once it is supported
    countryVals = ["India"]
    disciplineVals = ["Engineering"]
    levelVals = ["Undergraduation"]
    ############################################################################

            
    # Get the user object for the logged user
    usr = get_object_or_404(User, username=request.user)
    
    # Get the Querysets for the various preferences 
    cnt = Country.objects.filter(country_name__in=cntList)
    disc = Discipline.objects.filter(description__in=discList)
    level = Level.objects.filter(level_name__in=lvlList)
    prog = Program.objects.filter(description__in=progList)
    instt = Institute.objects.filter(instt_name__in=insttnmList)
    stuCat = StudentCategory.objects.filter(description__in=stuCatList)
    
    # Get Instt, prog and Student Category codes
    insttCode = instt.values("instt_code")
    progCode = prog.values("program_code")

    # Get the programs offered by selected Institutes
    insttProg = InstitutePrograms.objects.filter(Institute_id__in=insttCode, Program_id__in=progCode)
    
    msg = ''
    pass_fail = 'FAIL'

    
    try:
    
        if stuCat.exists():    
            # Delete the existing records for current user
            StudentCategoryUserPref.objects.filter(User=usr).delete()

            for s in stuCat :
                stuCatPref = StudentCategoryUserPref(StudentCategory = s, User = usr)
                stuCatPref.save()

        if cnt.exists():    
            # Delete the existing records for current user
            CountryUserPref.objects.filter(User=usr).delete()

            for c in cnt:
                cntPref = CountryUserPref(Country = c, User = usr)
                cntPref.save()
        
        if disc.exists():     
            
            # Delete the existing records for current user
            DisciplineUserPref.objects.filter(User=usr).delete()

            for c in disc:
                discPref = DisciplineUserPref(Discipline = c, User=usr)
                discPref.save()
                
        if level.exists():
            # Delete the existing records for current user
            LevelUserPref.objects.filter(User=usr).delete()

            for c in level:
                levelPref = LevelUserPref(Level = c, User=usr)
                levelPref.save()
    
        # Delete the existing records for current user
        ProgramUserPref.objects.filter(User=usr).delete()
        if prog.exists():
            for c in prog:
                progPref = ProgramUserPref(Program = c, User=usr)
                progPref.save()
                
        InsttUserPref.objects.filter(User=usr).delete()
        if instt.exists():
            for c in cnt:
                for d in disc:
                    if level.exists():
                        for l in level:
                            for i in instt:
                                if insttProg.exists():
                                    for ip in insttProg:
                                        if i.instt_code == ip.Institute_id:
                                            p = get_object_or_404(Program, program_code = ip.Program_id)
                                            insttPref = InsttUserPref(Country = c, Discipline = d, Level = l, Program = p, Institute = i, User=usr)
                                            insttPref.save()
                                else:
                                    insttPref = InsttUserPref(Country = c, Discipline = d, Level = l, Institute = i, User=usr)
                                    insttPref.save()
                                    
                    else: 
                        for i in instt:
                            if insttProg.exists():
                                for ip in insttProg:
                                    if i.instt_code == ip.Institute_id:
                                        p = get_object_or_404(Program, program_code = ip.Program_id)
                                        insttPref = InsttUserPref(Country = c, Discipline = d, Level = null, Program = p, Institute = i, User=usr)
                                        insttPref.save()
                            else:
                                insttPref = InsttUserPref(Country = c, Discipline = d, Level = l, Institute = i, User=usr)
                                insttPref.save()
                        
    
        #Set default as status PASS and the success message
        pass_fail = 'PASS'      
        msg = 'Your preferences are saved!!'

    except IntegrityError as e:
        msg = 'Apologies!! Could not save your preferences. Please use the contact us form at the bottom of this page to let us know your preferences.'
        pass_fail = 'FAIL'

    except Error as e:
        msg = 'Apologies!! Could not save your preferences. Please use the contact us form at the bottom of this page to let us know your preferences.'
        pass_fail = 'FAIL'
            
    return render(request, 'NextSteps/userPrefsConfirm.html', {
        'save':pass_fail, 'msg':msg})




# This method returns the user preferences in JSON.
# This method is used in Preferences(userPrefs.html) to get and set the user  
# selected preferences
# The userPrefs.html makes an AJAX call that gets routed here through the url.py 
# and this method returns the user preferences after extracting from DB models
def getInstitutes(request):

    countryVals = request.GET.get('cntList', 'Blank').split(";")
    disciplineVals = request.GET.get('discList', 'Blank').split(";")
    levelVals = request.GET.get('lvlList', 'Blank').split(";")
    programVals = request.GET.get('progList', 'Blank').split(";")

    usr = get_object_or_404(User, username=request.user)

    # Get all records first
    insttProgList = InstitutePrograms.objects.values('Institute__instt_name').distinct().order_by('Institute__instt_name')

    if countryVals != 'Blank' :
        cnt = Country.objects.filter(country_name__in=countryVals)
        insttProgList = insttProgList.filter(Country__in=cnt).values('Institute__instt_name').distinct().order_by('Institute__instt_name')
                
    if disciplineVals != 'Blank' :
        disc = Discipline.objects.filter(description__in=disciplineVals)
        insttProgList = insttProgList.filter(Discipline__in=disc).values('Institute__instt_name').distinct().order_by('Institute__instt_name')

    if levelVals != 'Blank' :
        lvl = Level.objects.filter(level_name__in=levelVals)
        insttProgList = insttProgList.filter(Level__in=lvl).values('Institute__instt_name').distinct().order_by('Institute__instt_name')

    if programVals != 'Blank' :
        prog = Program.objects.filter(description__in=programVals)
        insttProgList = insttProgList.filter(Program__in=prog).values('Institute__instt_name').distinct().order_by('Institute__instt_name')

    return JsonResponse(list(insttProgList), safe=False)    


def getPrograms(request):

    countryVals = request.GET.get('cntList', 'Blank').split(";")
    disciplineVals = request.GET.get('discList', 'Blank').split(";")
    levelVals = request.GET.get('levelList', 'Blank').split(";")

#    usr = get_object_or_404(User, username=request.user)

    # Get all records first
    progList = InstitutePrograms.objects.values('Program__description').distinct().order_by('Program__description')

    if countryVals != ['Blank']:
        cnt = Country.objects.filter(country_name__in=countryVals)
        progList = progList.filter(Country__in=cnt).values('Program__description').distinct().order_by('Program__description')
                
    if disciplineVals != ['Blank'] :
        disc = Discipline.objects.filter(description__in=disciplineVals)
        progList = progList.filter(Discipline__in=disc).values('Program__description').distinct().order_by('Program__description')

    if levelVals != ['Blank'] :
        level = Level.objects.filter(level_name__in=levelVals)
        progList = progList.filter(Level__in=level).values('Program__description').distinct().order_by('Program__description')

    return JsonResponse(list(progList), safe=False)    


def getSeatQuotaPrograms(request):

    countryVals = request.GET.get('cntList', 'Blank').split(";")
    disciplineVals = request.GET.get('discList', 'Blank').split(";")
    levelVals = request.GET.get('levelList', 'Blank').split(";")
    seatquotaVals = request.GET.get('seatquotaList', 'Blank').split(";")

#    usr = get_object_or_404(User, username=request.user)

    # Get all records first
    progList = InstituteProgramSeats.objects.values('Program__description').distinct().order_by('Program__description')


    if countryVals != [''] :
        cnt = Country.objects.filter(country_name__in=countryVals)
        progList = progList.filter(Country__in=cnt).values('Program__description').distinct().order_by('Program__description')
                
    if disciplineVals != [''] :
        disc = Discipline.objects.filter(description__in=disciplineVals)
        progList = progList.filter(Discipline__in=disc).values('Program__description').distinct().order_by('Program__description')

    if levelVals != [''] :
        level = Level.objects.filter(level_name__in=levelVals)
        progList = progList.filter(Level__in=level).values('Program__description').distinct().order_by('Program__description')

    if seatquotaVals != [''] :
        seatquota = StudentCategory.objects.filter(description__in=seatquotaVals)
        progList = progList.filter(StudentCategory__in=seatquota).values('Program__description').distinct().order_by('Program__description')

    return JsonResponse(list(progList), safe=False)    



@login_required
@subscription_active
def preferredInsttDetails(request):

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    # Get User preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    programUserList = ProgramUserPref.objects.filter(User__in=userid).order_by('Program__description')
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name','Institute__address_1', 'Institute__address_2',
        'Institute__address_3','Institute__city', 'Institute__state', 'Institute__pin_code',
        'Institute__phone_number','Institute__email_id','Institute__website',
        'Institute__InstituteType_id', 'Program__program_code').order_by(
            'Institute__Country', 'Institute__city', 'Institute__instt_name')

    insttNames = insttUserList.values('Institute__instt_name')

    # Get Institute Ids
    insttList = Institute.objects.filter(instt_name__in = insttNames).values('instt_code')

    # Get the preferred student category
    categoryUserList = StudentCategoryUserPref.objects.filter(User__in=userid).values('StudentCategory_id')

    # Get the program Details
    progUserList = InstituteProgramSeats.objects.filter(Institute_id__in = insttList, 
            StudentCategory_id__in = categoryUserList).values(
        'Institute__instt_code', 'Program__program_code', 'StudentCategory__description',
        'quota', 'number_of_seats')
            
#    from django.template.loader import render_to_string
#    import pdfkit
#    rendered = render_to_string('NextSteps/preferred_instt_details_PDF.html', {'insttUserList':insttUserList, 'progUserList':progUserList})
#    pdfkit.from_string(rendered, "prefInstt.pdf")

    return render(request, 'NextSteps/preferred_instt_details.html', 
            {'insttUserList':insttUserList, 'progUserList':progUserList})


@login_required
@subscription_active
def preferredInsttEntrance(request):

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    # Get User preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    programUserList = ProgramUserPref.objects.filter(User__in=userid).order_by('Program__description')
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name','Institute__address_1', 'Institute__address_2',
        'Institute__address_3','Institute__city', 'Institute__state', 'Institute__pin_code',
        'Institute__phone_number','Institute__email_id','Institute__website',
        'Institute__InstituteType_id', 'Program__program_code').order_by(
            'Institute__Country', 'Institute__city', 'Institute__instt_name')

    insttNames = insttUserList.values('Institute__instt_name')

    # Get Institute Ids
    insttList = Institute.objects.filter(instt_name__in = insttNames).values('instt_code')

    # Get the entrance exams Details
    entranceUserList = InstituteEntranceExam.objects.filter(Institute_id__in = insttList).values(
        'Institute__instt_code', 'EntranceExam__entrance_exam_code', 'EntranceExam__description')
    
    return render(request, 'NextSteps/preferred_instt_entrance.html', 
            {'insttUserList':insttUserList, 'entranceUserList':entranceUserList})


@login_required
@subscription_active
def preferredInsttImpDates(request):

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    # Get User preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    programUserList = ProgramUserPref.objects.filter(User__in=userid).order_by('Program__description')
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name','Institute__address_1', 'Institute__address_2',
        'Institute__address_3','Institute__city', 'Institute__state', 'Institute__pin_code',
        'Institute__phone_number','Institute__email_id','Institute__website',
        'Institute__InstituteType_id', 'Program__program_code').order_by(
            'Institute__Country', 'Institute__city', 'Institute__instt_name')

    insttNames = insttUserList.values('Institute__instt_name')

    # Get Institute Ids
    insttList = Institute.objects.filter(instt_name__in = insttNames).values('instt_code')
    
    #Get Program IDs
    progIdUser = programUserList.values('Program_id')


    # Get the imp dates details
    impDatesUserList = InstituteProgramImpDates.objects.filter(Institute_id__in = insttList, Program_id__in=progIdUser).values(
        'Institute__instt_code', 'Program__program_code', 'event', 'event_date', 'end_date', 'remarks').order_by('event_date')

    return render(request, 'NextSteps/preferred_instt_imp_dates.html', 
            {'insttUserList':insttUserList, 'impDatesUserList':impDatesUserList})





@login_required
@subscription_active
def preferredInsttAdmRoutes(request):

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')
    
    # Get User preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    programUserList = ProgramUserPref.objects.filter(User__in=userid).order_by('Program__description')
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name','Institute__address_1', 'Institute__address_2',
        'Institute__address_3','Institute__city', 'Institute__state', 'Institute__pin_code',
        'Institute__phone_number','Institute__email_id','Institute__website',
        'Institute__InstituteType_id').order_by(
            'Institute__Country', 'Institute__city', 'Institute__instt_name')

    insttNames = insttUserList.values('Institute__instt_name')

    # Get Institute Ids
    insttList = Institute.objects.filter(instt_name__in = insttNames).values('instt_code')

    # Get the adm route details
    admRoutesUserList = InstituteAdmRoutes.objects.filter(Institute_id__in = insttList).values(
        'Institute__instt_code', 'adm_route', 'description')
    
    return render(request, 'NextSteps/preferred_instt_adm_routes.html', 
            {'insttUserList':insttUserList, 'admRoutesUserList':admRoutesUserList})



@login_required
@subscription_active
def preferredInsttConsRep(request):

    usernm = request.user.get_username()
    filenm = usernm + "_preferredInstts.pdf"

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filenm


    buildConsRep(response, request)

    return response


@login_required
@subscription_active
def ifThenAnalysis(request):
     
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    # Get user country, discipline and level preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    countryList = countryUserList.values('Country_id')
    
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    disciplineList = disciplineUserList.values('Discipline_id')
    
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    levelList = levelUserList.values('Level_id')
    
    # Get the overall programs and institutes    
    #progList = InstitutePrograms.objects.values('Program__description').filter(
    #    Q(Institute__InstituteType_id = "IIT")| Q(Institute__InstituteType_id = "NIT") 
    #    ).values('Program__description')

    progList = InstitutePrograms.objects.values('Program__description').filter(
        Institute__jee_flag = "Y").values('Program__description')

        
    progList = progList.distinct().order_by('Program__description') 

        
    #insttList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
    #    Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
    #    ).values('Institute__instt_name')

    insttList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
        Institute__jee_flag = "Y") 
    
    insttList = insttList.distinct().order_by('Institute__instt_name')
    
    #stateList = InstitutePrograms.objects.values('Institute__state').filter(
    #    Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
    #    ).values('Institute__state').distinct().order_by('Institute__state')

    stateList = InstitutePrograms.objects.values('Institute__state').filter(
        Institute__jee_flag = "Y").values('Institute__state').distinct().order_by(
            'Institute__state')


    if countryList.exists() :
        progList = progList.filter(Country__in=countryList).values('Program__description').distinct().order_by('Program__description')
        insttList = insttList.filter(Country__in=countryList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')
                
    if disciplineList.exists() :
        progList = progList.filter(Discipline__in=disciplineList).values('Program__description').distinct().order_by('Program__description')
        insttList = insttList.filter(Discipline__in=disciplineList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')

    if levelList.exists() :
        progList = progList.filter(Level__in=levelList).values('Program__description').distinct().order_by('Program__description')
        insttList = insttList.filter(Level__in=levelList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')


    # Get the current USER program and institute preferences
    programUserList = ProgramUserPref.objects.filter(User__in=userid).values(
        'Program__description').distinct().order_by('Program__description')
    
    insttUserList = InsttUserPref.objects.filter(User__in=userid).filter(
        Institute__jee_flag = "Y").values(
        'Institute__instt_name',  'Institute__InstituteType').distinct().order_by('Institute__instt_name')
        
    stuCatList = StudentCategory.objects.filter(jee_flag = "Y")
    
    stuUserCat = StudentCategoryUserPref.objects.filter(User_id__in = userid)
    stuCategory = {}
    for c in stuUserCat:
        stuCategory = c.StudentCategory_id
    
    if stuCategory not in stuUserCat:
        validStuCat = False
    else:
        validStuCat = true
        
    
    return render(request, 'NextSteps/seat_chances_assessment.html', 
            {'programUserList':programUserList, 'insttUserList':insttUserList,
            'countryUserList':countryUserList, 'disciplineUserList':disciplineUserList,
            'levelUserList':levelUserList, 'progList':progList, 
            'insttList':insttList, 'stateList':stateList, 'stuCatList':stuCatList,
            'stuCategory':stuCategory, 'validStuCat':validStuCat })
    
    
@login_required
@subscription_active
def ifThenAnalysisResults(request):

    use_prefRadio = request.POST.get('use_prefRadio', 'BLANK')
    chooseProgsInstts = request.POST.get('chooseProgsInstts', 'BLANK')
    rankFrom= request.POST.get('rankFrom', 'BLANK')
    rankTo = request.POST.get('rankTo', 'BLANK')
    rankType = request.POST.get('mainAdvRadio', 'BLANK')
    homestate = request.POST.get('homestate', 'BLANK')
    #rankFromADVVal = request.POST.get('from1', 'BLANK')
    #rankToADVVal = request.POST.get('to1', 'BLANK')
    #progUserVals  = request.POST.getlist('progUserList', [])
    #insttUserVals = request.POST.getlist('insttUserList', [])
    progVals  = request.POST.getlist('progList', [])
    insttVals = request.POST.getlist('insttList', [])
    stuCategories = request.POST.getlist('stuCatSelect', [])
    stuUserCategory = request.POST.get('stuCategory', '')
    
    ''' If stuCategories is empty which mean user didn't select from the drop down
    then we use stuUserCaegory (preferred category) '''
    if stuCategories == []:
        stuCategories.append(stuUserCategory)

    # Get the student Category
    userid = User.objects.filter(username = request.user).values('id')
    #stuUserCat = StudentCategoryUserPref.objects.filter(User_id__in = userid)
 
    stuCat = StudentCategory.objects.filter(category__in = stuCategories)

    # Get max ranking year from DB
    max_year = InstituteJEERanks.objects.aggregate(Max('year'))
    maxyear = max_year['year__max']
    
    # Get user preferences. JEE is India specific and The Institute JEE Ranking table doesn't have Country,
    # hence not using the Country preference.
    if use_prefRadio == "ON" :
        disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid).values('Discipline_id')
        disciplineList = Discipline.objects.filter(discipline_code__in= disciplineUserList)
        
        levelUserList = LevelUserPref.objects.filter(User__in=userid).values('Level_id')
        levelList = Level.objects.filter(level_code__in= levelUserList)
        
        progUserList = InsttUserPref.objects.filter(User__in=userid).values('Program_id')
        progList = Program.objects.filter(program_code__in=progUserList)
        
        insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')
        insttList = Institute.objects.filter(instt_code__in=insttUserList)

    results = []
    
    # Start with all the programs and institutes and go with only the ranks
    if rankType == 'MAIN':
        #results = InstituteJEERanks.objects.filter( 
        #    Q( closing_rank__gte = rankFrom ) | Q( opening_rank__gte = rankFrom )).exclude(
        #    Institute__InstituteType_id = 'IIT').values('Discipline_id', 'Level_id',
        #    'Program_id', 'Institute__instt_name', 'Institute_id', 'Institute__state', 'year', 'opening_rank', 
        #    'closing_rank', 'quota').order_by('Program_id', 'closing_rank')

        results = InstituteJEERanks.objects.filter(Institute__jee_flag = "Y", year = maxyear,
            closing_rank__gte = rankFrom, opening_rank__gte = rankFrom ).exclude(
            Institute__InstituteType_id = 'IIT').values('Discipline_id', 'Level_id',
            'Program_id', 'Institute__instt_name', 'Institute_id', 'Institute__state', 'year', 'opening_rank', 
            'closing_rank', 'quota', 'StudentCategory_id').order_by('Program_id', 'closing_rank')

    
    if rankType == 'ADV':
        results = InstituteJEERanks.objects.filter( 
            Institute__jee_flag = "Y", Institute__InstituteType_id = 'IIT', year = maxyear,
            closing_rank__gte = rankFrom, opening_rank__gte = rankFrom).values(
            'Discipline_id', 'Level_id', 'Program_id', 'Institute_id', 
            'Institute__instt_name', 'Institute__state', 'year', 'opening_rank', 
            'closing_rank', 'quota', 'StudentCategory_id').order_by('Program_id', 'closing_rank')

    if len(progVals) > 0 :
        results = results.filter(Program__description__in=progVals ).order_by('Program_id', 'closing_rank')

    if len(insttVals) > 0 :
        results = results.filter(Institute__instt_name__in=insttVals ).order_by('Program_id', 'closing_rank')

    if stuCat.exists():
        results = results.filter(StudentCategory_id__in=stuCat).order_by('Program_id', 'closing_rank')
    
    err = False

    if results == [] :
        err = True
        results = InstituteJEERanks.objects.filter(Institute__instt_name__in=insttVals, year = maxyear).order_by('Program_id', 'closing_rank')


    #limiting results to 20 rows
    #results = results.filter()[:50]

    # let's apply the logic for "Homestate" in case of MAIN
    resultSet = []
    if rankType == 'MAIN':
        for r in results:
            if (r['Institute__state'] == homestate and r['quota'] == 'OS'):
                continue
            if (r['Institute__state'] != homestate and r['quota'] == 'HS'):
                continue
            this = {}
            this.update({'Program_id' : r['Program_id']})
            this.update({'Institute__instt_name' : r['Institute__instt_name']})
            this.update({'year': r['year']})
            this.update({'opening_rank': r['opening_rank']})
            this.update({'closing_rank': r['closing_rank']})
            this.update({'quota': r['quota']})
            this.update({'StudentCategory_id' : r['StudentCategory_id']})
            resultSet.append(this)
                    
    elif rankType == 'ADV':
        # converting Queryset to dict to keep it consistent with MAIN logic above
        for r in results:
            this = {}
            this.update({'Program_id' : r['Program_id']})
            this.update({'Institute__instt_name' : r['Institute__instt_name']})
            this.update({'year': r['year']})
            this.update({'opening_rank': r['opening_rank']})
            this.update({'closing_rank': r['closing_rank']})
            this.update({'quota': r['quota']})
            this.update({'StudentCategory_id' : r['StudentCategory_id']})
            resultSet.append(this)
    
    resultCnt = len(resultSet)
             
    return render(request, 'NextSteps/ifThenAnalysisResults.html', 
            {'resultSet':resultSet, 'err':err,'rankFrom':rankFrom, 
             'rankTo':rankTo, 'progs':progVals, 'instts':insttVals,
             'rankType':rankType, 'resultCnt':resultCnt, 'homestate':homestate,
             'stuCategories':stuCategories})     
    
 
def getUserInsttProgramByType(request):
    
    insttType = request.GET.get('insttType', 'Blank')
    insttOrProg= request.GET.get('insttOrProg', 'Blank')
    
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    # Get user preferences for country, discipline and level 
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    countryList = countryUserList.values('Country_id')
    
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    disciplineList = disciplineUserList.values('Discipline_id')
    
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    levelList = levelUserList.values('Level_id')
    
    if insttType == 'IIT':
        
        # Get the overall Programs and then apply filters
        progList = InsttUserPref.objects.filter(Institute__jee_flag = "Y",
            Institute__InstituteType_id = "IIT").values('Program__description')

        if countryList.exists() :
            progList = progList.filter(Country__in=countryList).values('Program__description')

        if disciplineList.exists() :
            progList = progList.filter(Discipline__in=disciplineList).values('Program__description')

        if levelList.exists() :
            progList = progList.filter(Level__in=levelList).values('Program__description')
            
        progList = progList.distinct().order_by('Program__description') 


        # Get the overall Institutes and then apply filters
        insttList = InsttUserPref.objects.filter(
            Institute__InstituteType_id = "IIT").values('Institute__instt_name')

        if countryList != [''] :
            insttList = insttList.filter(Country__in=countryList).values(
                'Institute__instt_name').distinct()

        if disciplineList != ['']:
            insttList = insttList.filter(Discipline__in=disciplineList).values(
                'Institute__instt_name').distinct()
        
        if levelList != [''] :
            insttList = insttList.filter(Level__in=levelList).values(
                'Institute__instt_name').distinct()
            
        insttList = insttList.distinct().order_by('Institute__instt_name') 
        
    else:
        # Get the overall Programs and then apply filters
        progList = InsttUserPref.objects.filter(Institute__jee_flag = "Y").exclude(
                Institute__InstituteType_id = "IIT").values('Program__description')

        if countryList != [''] :
            progList = progList.filter(Country__in=countryList).values('Program__description')

        if disciplineList != ['']  :
            progList = progList.filter(Discipline__in=disciplineList).values('Program__description')

        if levelList != ['']  :
            progList = progList.filter(Level__in=levelList).values('Program__description')

        progList = progList.distinct().order_by('Program__description') 

        # Get the overall Institutes and then apply filters
        insttList = InsttUserPref.objects.exclude(
                Institute__InstituteType_id = "IIT").filter(
                Institute__jee_flag = 'Y').values('Institute__instt_name')

        if countryList.exists() :
            insttList = insttList.filter(Country__in=countryList).values(
                'Institute__instt_name').distinct()
        if disciplineList.exists() :
            insttList = insttList.filter(Discipline__in=disciplineList).values(
                'Institute__instt_name').distinct()
        if levelList.exists() :
            insttList = insttList.filter(Level__in=levelList).values(
                'Institute__instt_name').distinct()
            

        insttList = insttList.distinct().order_by('Institute__instt_name') 
    

    
    if insttOrProg == "INSTT":
        return JsonResponse(list(insttList), safe=False)     
    else:
        return JsonResponse(list(progList), safe=False)     


def getInsttProgramByType(request):

    insttType = request.GET.get('insttType', 'Blank')
    insttOrProg= request.GET.get('insttOrProg', 'Blank')


    if insttType == 'IIT':
        
        # Get the overall Programs and then apply filters
        progList = InstitutePrograms.objects.filter(Institute__jee_flag = "Y", 
            Institute__InstituteType_id = "IIT").values(
                'Program__description').distinct().order_by('Program__description') 


        # Get the overall Institutes and then apply filters
        insttList = Institute.objects.filter(Institute__jee_flag = "Y", 
            InstituteType_id = "IIT").values('instt_name').distinct().order_by('instt_name')
        
    else:
        # Get the overall Programs and then apply filters
        progList = InstitutePrograms.objects.exclude(
            Institute__InstituteType_id = "IIT").filter(
                Institute__jee_flag = 'Y').values(
                    'Program__description').distinct().order_by('Program__description') 
    
        # Get the overall Institutes and then apply filters
        #insttList = InstitutePrograms.objects.exclude(
        #    Institute__InstituteType_id = "IIT").values('Institute__instt_name').distinct().order_by('Institute__instt_name') 
        
        insttList = Institute.objects.exclude(InstituteType_id = 'IIT').filter(
                jee_flag = 'Y').values('instt_name')

    
    if insttOrProg == "INSTT":
        return JsonResponse(list(insttList), safe=False)     
    else:
        return JsonResponse(list(progList), safe=False)   
    


@login_required
@subscription_active
def JEE_prog_instt_rank_filter(request):
    
    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    # Get user country, discipline and level preferences
    countryUserList = CountryUserPref.objects.filter(User__in=userid)
    countryList = countryUserList.values('Country_id')
    
    disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid)
    disciplineList = disciplineUserList.values('Discipline_id')
    
    levelUserList = LevelUserPref.objects.filter(User__in=userid)
    levelList = levelUserList.values('Level_id')
    
    # Get the overall programs and institutes    
    progList = InstitutePrograms.objects.values('Program__description').filter(
        Q(Institute__InstituteType_id = "IIT")| Q(Institute__InstituteType_id = "NIT") 
        ).values('Program__description')
        
    progList = progList.distinct().order_by('Program__description') 

        
    #insttProgList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
    #    Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
    #    ).values('Institute__instt_name')
    
    insttProgList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
        Institute__jee_flag = "Y").values('Institute__instt_name')
    
    
    insttProgList = insttProgList.distinct().order_by('Institute__instt_name')
    
    stateList = InstitutePrograms.objects.values('Institute__state').filter(
        Institute__jee_flag = "Y").values('Institute__state').distinct().order_by('Institute__state')

    if countryList.exists() :
        progList = progList.filter(Country__in=countryList).values(
            'Program__description').distinct().order_by('Program__description')
        
        insttProgList = insttProgList.filter(Country__in=countryList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')
                
    if disciplineList.exists() :
        progList = progList.filter(Discipline__in=disciplineList).values(
            'Program__description').distinct().order_by('Program__description')
        
        insttProgList = insttProgList.filter(Discipline__in=disciplineList).values(
            'Institute__instt_name',  
            'Institute__InstituteType').distinct().order_by('Institute__instt_name')

    if levelList.exists() :
        progList = progList.filter(Level__in=levelList).values(
            'Program__description').distinct().order_by('Program__description')
            
        insttProgList = insttProgList.filter(Level__in=levelList).values(
            'Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')


    # Get the current USER program and institute preferences
    programUserList = ProgramUserPref.objects.filter(User__in=userid).values(
        'Program__description').distinct().order_by('Program__description')
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values(
        'Institute__instt_name',  'Institute__InstituteType').distinct().order_by(
            'Institute__instt_name')
    
    '''
    return render(request, 'NextSteps/JEE_prog_instt_rank_filter.html', 
            {'programUserList':programUserList, 'insttUserList':insttUserList,
            'countryUserList':countryUserList, 'disciplineUserList':disciplineUserList,
            'levelUserList':levelUserList, 'progList':progList, 
            'insttProgList':insttProgList, 'stateList':stateList  })    
    '''
    return render(request, 'NextSteps/pref_jee_ranking.html', 
            {'programUserList':programUserList, 'insttUserList':insttUserList,
            'countryUserList':countryUserList, 'disciplineUserList':disciplineUserList,
            'levelUserList':levelUserList, 'progList':progList, 
            'insttProgList':insttProgList, 'stateList':stateList  })    


@login_required
@subscription_active
def JEE_prog_instt_rank_results(request):      

    optradio = request.POST.get('optradio', 'BLANK')
    optradio1 = request.POST.get('optradio1', 'BLANK')
    mainAdvRadio = request.POST.get('mainAdvRadio', 'BLANK')
    progUserVals  = request.POST.getlist('progUserList', [])
    insttUserVals = request.POST.getlist('insttUserList', [])
    progVals  = request.POST.getlist('progList', [])
    insttVals = request.POST.getlist('insttList', [])
    button = request.POST.get('submitbuttonMAIN', 'BLANK')
    homestate = request.POST.get('homestate', 'BLANK')
    button1 = request.POST.get("submitbuttonADV", 'BLANK')

    userid = User.objects.filter(username = request.user).values('id')
    
    if optradio == "ON":
        useUserPrefs = True
        progs = progUserVals
        instts = insttUserVals
        #progs = Program.objects.filter(description__in=progUserVals)
        #instts = Institute.objects.filter(instt_name__in=insttUserVals)
        
    if optradio == 'OFF':
        useUserPrefs = False
        progs = progVals
        instts = insttVals

    # Get user preferences. JEE is India specific and The Institute JEE Ranking table doesn't have Country,
    # hence not using the Country preference.
    if useUserPrefs :
        disciplineUserList = DisciplineUserPref.objects.filter(User__in=userid).values('Discipline_id')
        disciplineList = Discipline.objects.filter(discipline_code__in= disciplineUserList)
        
        levelUserList = LevelUserPref.objects.filter(User__in=userid).values('Level_id')
        levelList = Level.objects.filter(level_code__in= levelUserList)
        
        progUserList = InsttUserPref.objects.filter(User__in=userid).values('Program_id')
        progList = Program.objects.filter(program_code__in=progUserList)
        
        insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute_id')
        insttList = Institute.objects.filter(instt_code__in=insttUserList)
        
    if mainAdvRadio == "MAIN":
        rankType = 'MAIN'
    else:
        rankType = 'ADV'
    
    results = []
    
    # Start with all the programs and institutes and go with only the ranks
    if rankType == 'MAIN':
        results = InstituteJEERanks.objects.filter(Institute__jee_flag = "Y").exclude(
            Institute__InstituteType_id = 'IIT').values('Discipline_id', 'Level_id',
            'Program_id', 'year', 'Institute__instt_name', 'Institute_id', 'Institute__state', 'opening_rank', 
            'closing_rank', 'quota','StudentCategory_id').order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
    
    if rankType == 'ADV':
        results = InstituteJEERanks.objects.filter(Institute__jee_flag = "Y", 
            Institute__InstituteType_id = 'IIT').values(
            'Discipline_id', 'Level_id', 'Program_id', 'year', 'Institute_id', 
            'Institute__instt_name', 'Institute__state', 'opening_rank', 
            'closing_rank', 'quota','StudentCategory_id').order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')

    if len(progs) > 0 :
        results = results.filter(Program__description__in=progs ).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')

    if len(instts) > 0 :
        results = results.filter(Institute__instt_name__in=instts).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')

    err = False

    # if User preferences are being used, then filter the results for those.    
    if useUserPrefs:
        if disciplineList != ['']:
            results = results.filter(Discipline_id__in=disciplineList).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
        if levelList != ['']:
            results = results.filter(Level_id__in=levelList).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')

        if progs != ['']:
            results = results.filter(Program_id__in=progList).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
        if instts != ['']:
            results = results.filter(Institute_id__in=insttList).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
                

    if results == [] :
        err = True
        results = InstituteJEERanks.objects.filter(Institute__instt_name__in=instts).order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
    
    resultCnt = len(results)
             
    return render(request, 'NextSteps/JEE_prog_instt_rank_results.html', 
            {'results':results, 'err':err, 'progs':progs, 'instts':instts,
             'rankType':rankType, 'resultCnt':resultCnt})     
        
        
        
@login_required  
@subscription_active      
def userAppDetailsView(request):
    
    if request.method == 'POST':
        try:
            userid = User.objects.get(username = request.user)
            userObj = UserAppDetails.objects.get(User = userid)
            form = UserAppDetailsForm(request.POST, request.FILES, instance=userObj)
        except UserAppDetails.DoesNotExist:
            form = UserAppDetailsForm(request.POST, request.FILES)
            
        if form.is_valid():
            userapp = form.save(commit=False)
            userapp.User = request.user
            userapp.save()
            return redirect('user_app_confirm')
    else:
        try:
            userid = User.objects.get(username = request.user)
            userObj = UserAppDetails.objects.get(User = userid)                
            form = UserAppDetailsForm(instance=userObj)
            
        except UserAppDetails.DoesNotExist:
            
            try:
                userprofile = UserProfile.objects.get(User_id = userid)
                gender = userprofile.gender
                state_of_eligibility = userprofile.state
                address = userprofile.address
                city_town_village= userprofile.city
                state = userprofile.state
                phone_number = userprofile.phone_number
                email_id = userid.email
                form = UserAppDetailsForm(initial={'User': request.user, 
                    'gender':gender, 'state_of_eligibility': state_of_eligibility,
                    'address':address, 'city_town_village':city_town_village,
                    'state':state, 'phone_number':phone_number,
                    'email_id':email_id})
                
            except UserProfile.DoesNotExist:
                form = UserAppDetailsForm(initial={'User': request.user})
                
    return render(request, 'NextSteps/user_app_details_withWidgetTweaks.html', {
        'form': form    
    })
        
@subscription_active
def userAppDetailsConfirm(request):
    
    return render(request, 'NextSteps/userAppConfirm.html')

@login_required
@subscription_active
def studyPlanner(request, active_tab):

    userid = User.objects.filter(username = request.user).values('id')

    ''' current date '''
    today = datetime.date.today()
    
    ##### Get All Subject List
    cnt = request.POST.get('country', 'BLANK')
    disc = request.POST.get('discipline', 'BLANK')
    level = request.POST.get('level', 'BLANK')
    
    allSubjectList = Subjects.objects.all()
    
    if cnt != 'BLANK':
          allSubjectList  = allSubjectList .filter(Country__in = cnt)
        
    if disc != 'BLANK':
          allSubjectList  = allSubjectList .filter(Discipline__in = disc)

    if level != 'BLANK':
          allSubjectList  = allSubjectList .filter(Level__in = level)

    ## Let's get the UserStudySchedule
    #userSch = UserStudySchedule.objects.filter(User_id__in = userid).order_by('-date_updated')
    userSch = UserStudySchedule.objects.filter(User_id__in = userid).order_by('-id')
    
    # Get the latest user study schedule
    # There is going to be only one row for one user schedule, so we can use
    # the max of "id" column for the user to get latest schedule
    latest_userSch = UserStudySchedule.objects.filter(User_id__in = userid).order_by('-id')[:1]

    ### Get laster user Subject schedule
    # Here we need to get max datetime ('date_updated' column)it was updated,
    # and use that to get the latest subject schedule
    subjSchMax = UserSubjectSchedule.objects.filter(User_id__in = userid).aggregate(Max('date_updated'))
    maxdate = subjSchMax['date_updated__max']
    userSubjectList = UserSubjectSchedule.objects.filter(User_id__in = userid, 
                date_updated = maxdate)
    
    '''
    u = latest_userSch.objects.filter(User_id=OuterRef('study_hours_per_day'))
    s = UserSubjectSchedule.objects.annotate(subhrs=Subquery(s.values('User_id')[:1]))
    rawq = UserSubjectSchedule.objects.raw('SELECT a.subject,  (a.percentage_Weight * b.study_hours_per_day) as subjhrs FROM "NextSteps_usersubjectschedule" AS a, "NextSteps_userstudyschedule" AS b WHERE a."User_id" = 2 AND b."User_id" = 2 AND a."User_id" = b."User_id"')
    '''
        
    hrs = {}
    for s in userSubjectList:
        for l in latest_userSch:
            hrs[s.subject] = str(s.percentage_weight * l.study_hours_per_day / 100)
    subj_hrs = json.dumps(hrs)
    
    # Similary for Day Schdule
    daySchMax = UserDaySchedule.objects.filter(User_id__in = userid).aggregate(Max('date_updated'))
    maxDaySchdate = daySchMax['date_updated__max']
    userDaySch = UserDaySchedule.objects.filter(User_id__in = userid, date_updated = maxDaySchdate)

    ######### Date required in other tabs ##############
    # Get all Months
    monthsQueryset =  StudyHours.objects.annotate( year=Extract('date','year'), 
        month=Extract('date', 'month') ).values('month', 'year').distinct()
    
    import calendar

    # get month names
    months = [];
    for i in monthsQueryset:
        mth = calendar.month_abbr[int(i['month'])]
        yr = i['year']
        
        rec = {'month' : mth}
        rec['year'] = yr
        months.append(rec)
        
    # Get Dates from and to
    dateMin = StudyHours.objects.filter(User_id__in = userid).aggregate(Min('date'))
    dateMax = StudyHours.objects.filter(User_id__in = userid).aggregate(Max('date'))

    actualHrsMaxDate = StudyHours.objects.filter(User_id__in = userid).exclude(
        actual_hours__isnull=True).exclude(actual_hours__lte=0).aggregate(
            Max('date') )
    
    # Get the study hours - planned Vs actual 
    hrsPlannedOverall = StudyHours.objects.filter(User_id__in = userid, date__lte = today ).aggregate( 
            planned_hours__sum=Coalesce(Sum('planned_hours'),0))
    hrsActualOverall = StudyHours.objects.filter(User_id__in = userid, date__lte = today).aggregate( 
            actual_hours__sum=Coalesce(Sum('actual_hours'),0) )
    # Get the subjectwise study hours - planned Vs actual 
    hrsPlannedSubj = StudyHours.objects.filter(User_id__in = userid, date__lte = today).values(
            'subject').annotate(Sum('planned_hours')).order_by('subject')
    hrsActualSubj = StudyHours.objects.filter(User_id__in = userid, date__lte = today).values(
        'subject').annotate(actual_hours=Coalesce(Sum('actual_hours'), 0)).order_by('subject')


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ''' Check if schedule calendar needs to be generated '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''
    Get laster user day schedule
    Here we need to get max datetime ('date_updated' column),
    and use that to get the latest day schedule
    '''
    daySchMax = UserDaySchedule.objects.filter(User_id__in = userid).aggregate(Max('date_updated'))
    maxDaySchDate = daySchMax['date_updated__max']
    daySchGen = UserDaySchedule.objects.filter(User_id__in = userid, date_updated = maxDaySchDate, schedule_generated = False)
    daySchGenFlag = False
    
    if daySchGen:
        daySchGenFlag = True
    

    ''' Get subject wise percentage of actual hours compared to overall hours '''
    subjPercentage = {}
    perc = 0
    
    for i in userSubjectList:
        for j in hrsActualSubj:
            if (i.subject == j['subject']) :
                if float(hrsActualOverall['actual_hours__sum']) != 0:
                    perc = float(j['actual_hours']) * 100 / float(hrsActualOverall['actual_hours__sum'])
                else:
                    perc = 0
                subjPercentage[j['subject']] = perc
    
    # Get the subjectwise study hours - planned Vs actual 
    hrsPlannedMonth = StudyHours.objects.filter(User_id__in = userid).values(month=Extract(
        'date', 'month')).annotate(Sum('planned_hours')).order_by('month')
    hrsActualMonth = StudyHours.objects.filter(User_id__in = userid).values(month=Extract(
        'date', 'month')).annotate(Sum('actual_hours')).order_by('month')
    # Get the subjectwise study hours - planned Vs actual 
    hrsPlannedWeek = StudyHours.objects.filter(User_id__in = userid).values(week=Extract(
        'date', 'week')).annotate(Sum('planned_hours')).order_by('week')
    hrsActualWeek = StudyHours.objects.filter(User_id__in = userid).values(week=Extract(
        'date', 'week')).annotate(Sum('actual_hours')).order_by('week')

    # Setting current month and year
    currMonth = str(today.month)
    currYear = str(today.year)

    # Get the study hours for logging tab
    schStudyHrs = StudyHours.objects.filter(User_id__in = userid,
                date__month=currMonth, date__year=currYear ).order_by('date')

    
    #currMonth = str(datetime.now().month)
    #currYear = str(datetime.now().year)

    ### Form for Subject Schedule
    if request.method == 'POST':
        form = UserSubjectScheduleForm(request.POST)
        if form.is_valid():
            subj = form.save(commit=False)
            subj.User = request.user
            subj.save()            
            ####return redirect('referNextSteps_confirm')  
    else:
        ##form = UserSubjectScheduleForm()    
        try:
            requserid = User.objects.get(username = request.user)
            #userObj = UserSubjectSchedule.objects.filter(User = userid)
            #form = UserSubjectScheduleForm(initial = userObj)
            UserSubFormSet = modelformset_factory(UserSubjectSchedule, fields=('subject',
                    'percentage_weight','start_date', 'end_date') ) 
            form = UserSubFormSet(queryset=UserSubjectSchedule.objects.filter(User=requserid ))
            

        except UserSubjectSchedule.DoesNotExist:
            form = UserSubjectScheduleForm()
        
    return render(request, 'NextSteps/study_planner.html', {'allSubjectList':
            allSubjectList, 'userSubjectList':userSubjectList, 'form':form,
            'userSch': userSch, 'userDaySch' : userDaySch,'months':months, 
            'dateMin':dateMin, 'dateMax':dateMax, 'currMonth':currMonth, 
            'currYear':currYear, 'active_tab':active_tab,
            'hrsPlannedOverall':hrsPlannedOverall, 'hrsActualOverall':
            hrsActualOverall, 'hrsPlannedSubj':hrsPlannedSubj,
            'hrsActualSubj':hrsActualSubj, 'subjPercentage':subjPercentage,
            'latest_userSch':latest_userSch, 'actualHrsMaxDate':actualHrsMaxDate,
            'subj_hrs':subj_hrs, 'daySchGen':daySchGen, 'schStudyHrs':schStudyHrs})


@login_required
@subscription_active
def getUserSubjectSchedule(request):

    userid = User.objects.filter(username = request.user).values('id')

    ### Get user Subjects
    userSubjectList = UserSubjectSchedule.objects.filter(User_id__in = userid).values(
        'subject', 'percentage_weight', 'start_date', 'end_date')
    
    
    return JsonResponse(list(userSubjectList), safe=False)    

@subscription_active
def getStudyHours(request):
    month = request.GET.get('month', "")
    year = request.GET.get('year', "")
    
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")
    
    userid = User.objects.filter(username = request.user).values('id')

    # Create the base queryset and then apply each filter
    userStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
        'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
        'actual_hours').order_by('date', 'start_time')
    
    if (month != ""):
        userStudyHours = userStudyHours .filter(date__month=month).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date', 'start_time')

    if (year != ""):
        userStudyHours = userStudyHours.filter( date__year=year).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date', 'start_time')

    if (datefrom != ""):
        fromdate = datetime.datetime.strptime(datefrom, "%Y-%m-%d").date()
        userStudyHours = userStudyHours.filter( date__gte = fromdate).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date', 'start_time')
        
    if (dateto != ""):
        todate = datetime.datetime.strptime(dateto, "%Y-%m-%d").date()
        userStudyHours = userStudyHours.filter( date__lte = todate).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date', 'start_time')

    return JsonResponse(list(userStudyHours), safe=False)    

@subscription_active
def getMonthStudyHours(request):
    month = request.GET.get('month', "")
    year = request.GET.get('year', "")
    
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")
    
    userid = User.objects.filter(username = request.user).values('id')


    # Create the base queryset and then apply each filter
    monthStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
        'date').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date')
    
    if (month != ""):
        monthStudyHours = monthStudyHours .filter(date__month=month).values(
        'date').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date')


    if (year != ""):
        monthStudyHours = monthStudyHours.filter( date__year=year).values(
        'date').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date')


    if (datefrom != ""):
        fromdate = datetime.datetime.strptime(datefrom, "%Y-%m-%d").values(
        'date').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date')

        
    if (dateto != ""):
        todate = datetime.datetime.strptime(dateto, "%Y-%m-%d").date()
        monthStudyHours = monthStudyHours.filter( date__lte = todate).values(
        'date').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date')

    return JsonResponse(list(monthStudyHours), safe=False)   


@subscription_active
def getMonthSubjHours(request):
    month = request.GET.get('month', "")
    year = request.GET.get('year', "")
    
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")
    
    userid = User.objects.filter(username = request.user).values('id')

    # Create the base queryset and then apply each filter
    monthStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')
    
    
    if (month != ""):
        monthStudyHours = monthStudyHours .filter(date__month=month).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (year != ""):
        monthStudyHours = monthStudyHours.filter( date__year=year).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (datefrom != ""):
        fromdate = datetime.datetime.strptime(datefrom, "%Y-%m-%d").date()
        monthStudyHours = monthStudyHours.filter( date__gte = fromdate).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (dateto != ""):
        todate = datetime.datetime.strptime(dateto, "%Y-%m-%d").date()
        monthStudyHours = monthStudyHours.filter( date__lte = todate).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')
    

    return JsonResponse(list(monthStudyHours), safe=False)    


@subscription_active
# This function is used by the Study Planner -> Dashboard - > Stacked Column CHart
def getDayRows(request):
    month = request.GET.get('month', "")
    year = request.GET.get('year', "")
    
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")
    
    userid = User.objects.filter(username = request.user).values('id')
    monthStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    
    subjsArray = StudyHours.objects.filter( User_id__in = userid).values(
        'subject').distinct()
        
    datesHrs =  StudyHours.objects.filter( User_id__in = userid).values(
        'date').distinct()   

    if (month != ""):
        datesHrs = datesHrs .filter(date__month=month).values('date')
        monthStudyHours = monthStudyHours .filter(date__month=month).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (year != ""):
        datesHrs = datesHrs.filter( date__year=year).values('date')
        monthStudyHours = monthStudyHours.filter( date__year=year).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (datefrom != ""):
        fromdate = datetime.datetime.strptime(datefrom, "%Y-%m-%d").date()
        datesHrs = datesHrs.filter( date__gte = fromdate).values('date')
        fromdate = datetime.datetime.strptime(datefrom, "%Y-%m-%d").date()
        monthStudyHours = monthStudyHours.filter( date__gte = fromdate).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')

    if (dateto != ""):
        todate = datetime.datetime.strptime(dateto, "%Y-%m-%d").date()
        datesHrs = datesHrs.filter( date__lte = todate).values('date')
        todate = datetime.datetime.strptime(dateto, "%Y-%m-%d").date()
        monthStudyHours = monthStudyHours.filter( date__lte = todate).values(
        'date', 'subject').annotate( Sum('planned_hours'), Sum('actual_hours') ).order_by('date','subject')
    
    
    #subjsArray = monthStudyHours.values('subject').distinct()
    datesArray = datesHrs.dates('date', 'day').distinct()
    dayrows = []
    row = []
    data = []

    # create first row
    firstrow = []
    firstrow.append('Date')
    for s in subjsArray:
        firstrow.append(s['subject']);
    #last piece data
    d = {'role': 'annotation'}
    firstrow.append(d)
    
    data.append(firstrow)

    
    for d in datesArray:
        #row.append(d['date'])
        dt = d.strftime("%d-%b")
        row.append(dt)
            
        for s in subjsArray:
            # Search for this subject and date in monthStudyHours and if found
            # add the actual hours, otherwise need add a blank for this subject 
            #and date
            subFound = False
            
            for m in monthStudyHours:
                #if (s['subject'] == m['subject'] and d['date'] == m['date']):
                if (s['subject'] == m['subject'] and d == m['date']):
                    row.append(m['actual_hours__sum'])
                    subFound = True
            
            if subFound == False:
                row.append('')
            
            subFound = False

        # Need to add a blank at the end (as per the stacked column chart to be
        # displayed 
        row.append('')
        
        data.append(row)
        row = []
    
    return JsonResponse(list(data), safe=False)    


@login_required
@subscription_active
def printStudySchedule(request):

    month = request.POST.get('month', "")
    year = request.POST.get('year', "")
    
    userid = User.objects.filter(username = request.user).values('id')

    if (month == "" or year == ""):
        userStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date')
    else:
        userStudyHours = StudyHours.objects.filter( User_id__in = userid,
            date__month=month, date__year=year).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date', 'start_time')
    
    # Get all Months
    monthsQueryset =  StudyHours.objects.annotate( year=Extract('date','year'), 
        month=Extract('date', 'month') ).values('month', 'year').distinct()
    
    import calendar

    # get month names
    months = [];
    for i in monthsQueryset:
        mth = calendar.month_abbr[int(i['month'])]
        yr = i['year']
        
        rec = {'month' : mth}
        rec['year'] = yr
        months.append(rec)
        
    # Get Dates from and to
    dateMin = StudyHours.objects.all().aggregate(Min('date'));
    dateMax = StudyHours.objects.all().aggregate(Max('date'));
    
    # Setting current month to a string value
    currMonth = calendar.month_abbr[int(month)]

    '''    
    return render(request, 'NextSteps/printStudySchedule.html', 
        {'userStudyHours': userStudyHours, 'months':months, 'dateMin':dateMin,
         'dateMax':dateMax, 'currMonth':currMonth, 'currYear':year})
    '''
    return render(request, 'NextSteps/print_study_schedule.html', 
        {'userStudyHours': userStudyHours, 'months':months, 'dateMin':dateMin,
         'dateMax':dateMax, 'currMonth':currMonth, 'currYear':year})



''' Saving the Schedule Calendar '''
@csrf_exempt
def saveStudyHours (request):
    
    if request.is_ajax():
        if request.method == 'POST':

            # Get data from the request.
            json_data = json.loads(request.body.decode("utf-8"))

            # Get the user object for the logged in user
            usr = get_object_or_404(User, username=request.user)

            # delete the existing data
            StudyHours.objects.filter(User=usr).delete()
            
            pass_fail = 'PASS'
            msg = 'SUCCESS'

            today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for i in json_data:
                start = i.get("start", "")
                end = i.get("end", "")
                
                subject = i.get("subject", "")
                start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
                end_date = None
                if end != ('' or None):
                    end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")

                start_time = i.get("start_time", "")
                end_time = i.get("end_time", "")
                planned_hours = i.get("planned_hours", "")
                actual_hours = i.get("actual_hours", "")

                # if end_date is not none, then we loop through all days between start and end and insert one row for each day.
                if end_date != ('' or None):
                    
                    # loop through each date between start and end dates, we will insert one row for each day
                    day_count = (end_date - start_date).days + 1
                    for single_date in (start_date + timedelta(n) for n in range(day_count)):
                        date = single_date.strftime("%Y-%m-%d")
    
                        try: 
                            
                            # save the data
                            studyhours  = StudyHours(User = usr, subject = subject, 
                                        date = date, start_time= start_time, 
                                        end_time= end_time, planned_hours= planned_hours,
                                        date_updated = today) 
                            studyhours .save()
            
                        except IntegrityError as e:
                            pass_fail = 'FAIL'
                            
                        except Error as e:
                            pass_fail = 'FAIL'
                else :
                    try: 
                                
                        # save the data
                        
                        studyhours  = StudyHours(User = usr, subject = subject, 
                                    date = start_date, start_time= start_time, 
                                    end_time= end_time, planned_hours= planned_hours,
                                    date_updated = today) 
                        studyhours .save()
        
                    except IntegrityError as e:
                        pass_fail = 'FAIL'
                        
                    except Error as e:
                        pass_fail = 'FAIL'
                    

    return HttpResponse(pass_fail)
    
''' Saving the actual hours logged '''
@csrf_exempt
def saveLoggedHours(request):
    if request.is_ajax():
        if request.method == 'POST':

            # Get data from the request.
            json_data = json.loads(request.body.decode("utf-8"))

            # Get the user object for the logged in user
            usr = get_object_or_404(User, username=request.user)

            # delete the existing data
            #StudyHours.objects.filter(User=usr).delete()
            
            pass_fail = 'PASS'
            msg = 'SUCCESS'

            today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for i in json_data:
               
                id = i.get("id", "")
                subject = i.get("subject", "")
                dt = i.get("date", "")
                date = datetime.datetime.strptime(dt, "%Y-%m-%d")
                start_time = i.get("start_time", "")
                end_time = i.get("end_time", "")
                planned_hours = i.get("planned_hours", "")
                actual_hours = i.get("actual_hours", "")
               
                if actual_hours == "None" or actual_hours == "Empty" or actual_hours == "":
                    continue

                try: 
                    # save the data
                    studyhours  = StudyHours(
                                id = int(id), 
                                User = usr, 
                                subject = subject, 
                                date = date, 
                                start_time= start_time, 
                                end_time= end_time, 
                                planned_hours= planned_hours,
                                actual_hours = actual_hours,
                                date_updated = today
                                ) 
                    studyhours.save(force_update = True)
    
                except IntegrityError as e:
                    pass_fail = 'FAIL'
                    
                except Error as e:
                    pass_fail = 'FAIL'
                

    return HttpResponse(pass_fail)
    


@login_required
@subscription_active
def updateStudySchedule(request):

    month = request.POST.get('month', "")
    year = request.POST.get('year', "")
    
    userid = User.objects.filter(username = request.user).values('id')

    if (month == "" or year == ""):
        userStudyHours = StudyHours.objects.filter( User_id__in = userid).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date')
    else:
        userStudyHours = StudyHours.objects.filter( User_id__in = userid,
            date__month=month, date__year=year).values(
            'id', 'subject', 'date', 'start_time', 'end_time', 'planned_hours', 
            'actual_hours').order_by('date')
    
    # Get all Months
    monthsQueryset =  StudyHours.objects.annotate( year=Extract('date','year'), 
        month=Extract('date', 'month') ).values('month', 'year').distinct()
    
    
    import calendar

    # get month names
    months = [];
    for i in monthsQueryset:
        mth = calendar.month_abbr[int(i['month'])]
        yr = i['year']
        
        rec = {'month' : mth}
        rec['year'] = yr
        months.append(rec)
        
    # Get Dates from and to
    dateMin = StudyHours.objects.all().aggregate(Min('date'));
    dateMax = StudyHours.objects.all().aggregate(Max('date'));
    
    # Setting current month to a string value
    currMonth = calendar.month_abbr[int(month)]
    
    return render(request, 'NextSteps/updateStudySchedule.html', 
        {'userStudyHours': userStudyHours, 'months':months, 'dateMin':dateMin,
         'dateMax':dateMax, 'currMonth':currMonth, 'currYear':year})
    
@login_required
@subscription_active
def saveStudySchedule(request):

    days = request.GET.get('daysperweek', "")
    daysperweek = int(days)
    hrs = request.GET.get('hrsperday', "")
    hrsperday = int(hrs)
    start = request.GET.get('startDt', "")
    startDt = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end = request.GET.get('endDt', "")
    endDt = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    pass_fail = 'FAIL'
    msg = ''
  
    # Get the user object for the logged user
    usr = get_object_or_404(User, username=request.user)
    
    try:
        NewStudySch = UserStudySchedule(User = usr, 
                            study_days_per_week = daysperweek,
                            study_hours_per_day = hrsperday,
                            start_date = startDt,
                            end_date = endDt,
                            date_updated = today)
        NewStudySch.save()
        pass_fail = 'PASS'
        
        
    except IntegrityError as e:
        msg = 'Apologies!! Could not save your preferences. Please use the "Contact Us" link at the bottom of this page and let us know. We will glad to help you.'
        pass_fail = 'FAIL'

    except Error as e:
        msg = 'Apologies!! Could not save your preferences. Please use the "Contact Us" link at the bottom of this page and let us know. We will glad to help you.'
        pass_fail = 'FAIL'

    return JsonResponse(msg, safe=False)    
            
@login_required
@subscription_active
def saveSubjSch(request):
        
    rows = request.GET.getlist('rows[]', [])

    if not rows:
        msg = 'Nothing to Save'
        return JsonResponse(msg, safe=False)    
    
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = 'Your subject schedule is saved successfully'
  
    # Get the user object for the logged user
    usr = get_object_or_404(User, username=request.user)
    
    # Get existing study schedule for the user
    
    try :
        for r in rows:
            
            row = r.split(",")
            
            start_date = datetime.datetime.strptime(row[2], "%d %b %Y").date()
            end_date = datetime.datetime.strptime(row[3], "%d %b %Y").date()
            newSubjSch = UserSubjectSchedule(User = usr,
                                            subject = row[0],
                                            percentage_weight = int(row[1]),
                                            start_date = start_date,
                                            end_date = end_date,
                                            date_updated = today)
            newSubjSch.save()

    except IntegrityError as e:
        msg = 'Apologies!! Could not save your subject schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    except Error as e:
        msg = 'Apologies!! Could not save your subject schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    return JsonResponse(msg, safe=False)    

@login_required
@subscription_active
def saveDaySch(request):
    
    rows = request.GET.getlist('day_data[]', [])
    days_of_week = request.GET.getlist('days_of_week[]', [])

    if not rows:
        msg = 'Update the data to save'
        return JsonResponse(msg, safe=False)    
    if not days_of_week:
        msg = 'Days of the week not selected'
        return JsonResponse(msg, safe=False)    
    
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = 'Your day schedule is saved successfully'
    
    mon=tue=wed=thu=fri=sat=sun = False
    for d in days_of_week:
        if d == '0':
            mon = True
            continue
        if d == '1':
            tue = True
            continue
        if d == '2':
            wed = True
            continue
        if d == '3':
            thu = True
            continue
        if d == '4':
            fri = True
            continue
        if d == '5':
            sat = True
            continue
        if d == '6':
            sun = True
            continue
  
    # Get the user object for the logged user
    usr = get_object_or_404(User, username=request.user)
    
    try :
        for r in rows:
            
            row = r.split(",")
            
            start_time = datetime.datetime.strptime(row[1], "%H:%M")
            end_time = datetime.datetime.strptime(row[2], "%H:%M")
            newDaySch = UserDaySchedule(User = usr,
                                subject = row[0],
                                start_time = start_time,
                                end_time = end_time,
                                planned_hours = float(row[3]),
                                date_updated = today,
                                mon = mon,
                                tue = tue,
                                wed = wed,
                                thu = thu,
                                fri = fri,
                                sat = sat,
                                sun = sun)
            newDaySch.save()

    except IntegrityError as e:
        msg = 'Apologies!! Could not save your day schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    except Error as e:
        msg = 'Apologies!! Could not save day schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    return JsonResponse(msg, safe=False)    

@login_required
@subscription_active
def generateSchCalendar (request):

    # Get the user object for the logged user
    usr = get_object_or_404(User, username=request.user)
    userid = User.objects.filter(username = request.user).values('id')
     
    '''
    Get laster user Subject schedule
    Here we need to get max datetime ('date_updated' column),
    and use that to get the latest subject schedule
    '''
    subjSchMax = UserSubjectSchedule.objects.filter(User_id__in = userid).aggregate(Max('date_updated'))
    maxdate = subjSchMax['date_updated__max']
    userSubSch = UserSubjectSchedule.objects.filter(User_id__in = userid, 
                date_updated = maxdate)

    '''
    Get laster user day schedule
    Here we need to get max datetime ('date_updated' column),
    and use that to get the latest day schedule
    '''
    daySchMax = UserDaySchedule.objects.filter(User_id__in = userid).aggregate(Max('date_updated'))
    maxDaySchDate = daySchMax['date_updated__max']
    daySch = UserDaySchedule.objects.filter(User_id__in = userid, date_updated = maxDaySchDate)
    
    if not userSubSch:
        msg = 'No schedule found to be generated. Have you updated Subject Schedule yet?'
        return JsonResponse(msg, safe=False)    
    
    if not daySch:
        msg = 'No schedule found to be generated. Have you updated Day Schedule yet?'
        return JsonResponse(msg, safe=False)    

    days_of_week = []
    
    for u in daySch:
        if u.mon :
            days_of_week.append('0')
        if u.tue :
            days_of_week.append('1')
        if u.wed:
            days_of_week.append('2')
        if u.thu :
            days_of_week.append('3')
        if u.fri :
            days_of_week.append('4')
        if u.sat :
            days_of_week.append('5')
        if u.sun :
            days_of_week.append('6')
        break; ''' All subjects would have the same days, so no need go through rest of the rows'''

    if not days_of_week:
        msg = 'No study days found in Day Schedule to be able to generate the schedule. Please update Day Schedule with days of week.'
        return JsonResponse(msg, safe=False)    

    #rows = request.GET.getlist('day_data_with_dates[]', [])
    #days_of_week = request.GET.getlist('days_of_week[]', [])
    
    msg = ''
    #mon=tue=wed=thu=fri=sat=sun = False
    
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    ''' Let's get the latest date which user has entered the actual hours.'''
    actDateMax = StudyHours.objects.filter(User_id__in = userid, actual_hours__gt = 0).aggregate(Max('date'))
    dtMax = actDateMax['date__max']
    
    try :
        #for r in rows:
        for r in userSubSch:
            #row = r.split(",")

            #start_date = datetime.datetime.strptime(row[1], "%Y-%m-%d").date() 
            #end_date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()

            ''' We update the planned hours only from actual_hours date, if present '''
            ''' We won't overwrite if the actual hours are already entered'''
            dateFrom = r.start_date 
            if dtMax:
                if dtMax > r.start_date:
                     dateFrom = dtMax + datetime.timedelta(days=1)
                     
            for single_date in daterange(dateFrom, r.end_date):
                #dt = datetime.datetime.strptime(single_date, "%Y-%m-%d").date()
                #single_date.strftime("%Y-%m-%d").date()

                ''' if this day is NOT planned as study day by user, then continue with next date'''
                if not str(single_date.weekday()) in days_of_week:
                    continue

                startTime = datetime.time(0, 0)
                endTime = datetime.time(0, 0)
                plannedHours = 0

                '''Get start, end time, and planned_hours from DaySch'''
                ''' Day Sch is already filtered for the current user and the latest schedule date'''
                ''' filtering further on subject should yield only one row '''
                thisDaySch = daySch.filter(subject = r.subject)
                for t in thisDaySch:
                    startTime = t.start_time
                    endTime = t.end_time
                    plannedHours = t.planned_hours
                    updID = t.id
                    dtUpdated = t.date_updated

                #start_time = datetime.datetime.strptime(row[3], "%H:%M")
                #end_time = datetime.datetime.strptime(row[4], "%H:%M")

                ''' Get date to check if the row for this date already exists '''
                #existing_data = StudyHours.objects.filter(User_id__in = userid,
                #            date = single_date, subject = row[0] )
                existing_data = StudyHours.objects.filter(User_id__in = userid,
                            date = single_date, subject = r.subject )
                
                rec_id = randrange(1000000000)
                ''' StudyHours will have only have 1 row for a user, a subject and a date'''
                for d in existing_data:
                    rec_id = d.id
    
                # data coming in....
                #day_rec_with_dates = [subj, lstart_date, lend_date, starttime, endtime, planned_hours];
                if existing_data:
                    newSch = StudyHours(
                                    id = rec_id,
                                    User = usr,
                                    subject = r.subject,
                                    date = single_date,
                                    start_time = startTime,
                                    end_time = endTime,
                                    planned_hours = plannedHours,
                                    date_updated = today)
                    newSch.save(force_update=True)
                else:
                    newSch = StudyHours(
                                    User = usr,
                                    subject = r.subject,
                                    date = single_date,
                                    start_time = startTime,
                                    end_time = endTime,
                                    planned_hours = plannedHours,
                                    date_updated = today)
                    newSch.save(force_insert=True)

                    
                '''Update the schedule generated flag in day schedule'''
                daySchUpd = UserDaySchedule(
                                id = updID,
                                User = usr,
                                subject = r.subject,
                                start_time = startTime,
                                end_time = endTime,
                                planned_hours = plannedHours,
                                date_updated = dtUpdated,
                                schedule_generated = True,
                                schedule_generated_date = today)
                daySchUpd.save(force_update = True)
                    
            msg = 'Schedule Calendar is generated successfully'
                
    except IntegrityError as e:
        msg = 'Apologies!! Could not save your day schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    except Error as e:
        msg = 'Apologies!! Could not save day schedule. Please use the "Contact Us" link at the bottom of this page and let us know. We will be glad to help you.'

    return JsonResponse(msg, safe=False)    



def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def instt_prog_group_lookup(request):
    
    return render(request, 'NextSteps/instt_prog_group_lookup1.html') 



def get_instt_prog_group(request):
    
    progGrpVal = request.GET.get('progGrpVal')
    
    progs_group = InstitutePrograms.objects.all().order_by ('Program__program_group').values(
        'Program__program_group', 'Program_id', 'Institute__instt_name')

    print(progGrpVal)

    
    if progGrpVal :
        progs_group = progs_group.filter(Program__program_group__icontains = progGrpVal)

    '''
    paginator = Paginator(progs_group, 20) 
    page = request.GET.get('page')
    progs = paginator.get_page(page)
    '''

    return render(request, 'NextSteps/get_instt_prog_group.html', {'progs':progs_group}) 

