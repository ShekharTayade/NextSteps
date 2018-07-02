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

from NextSteps.forms import SignUpForm, UserAppDetailsForm
from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import Country, Discipline, Level, Program, InstitutePrograms
from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref
from NextSteps.models import ProgramUserPref, InsttUserPref, InstituteProgramSeats
from NextSteps.models import InstituteEntranceExam, InstituteProgramImpDates
from NextSteps.models import StudentCategory, StudentCategoryUserPref, InstituteAdmRoutes
from NextSteps.models import UserAppDetails, UserProfile

from .common_views import *
from .pdf_views import *

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
                    Program_id__in=progList ).values(
                        'Institute__instt_name').distinct().order_by('Institute__instt_name')
    else:
        insttList = InstitutePrograms.objects.filter(Country__in = countryCodes, 
                    Discipline__in=disciplineCodes, Level__in=levelCodes).values(
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


    if countryVals != 'Blank' :
        cnt = Country.objects.filter(country_name__in=countryVals)
        progList = progList.filter(Country__in=cnt).values('Program__description').distinct().order_by('Program__description')
                
    if disciplineVals != 'Blank' :
        disc = Discipline.objects.filter(description__in=disciplineVals)
        progList = progList.filter(Discipline__in=disc).values('Program__description').distinct().order_by('Program__description')

    if levelVals != 'Blank' :
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


    print("progIdUser")
    print(progIdUser)

    # Get the imp dates details
    impDatesUserList = InstituteProgramImpDates.objects.filter(Institute_id__in = insttList, Program_id__in=progIdUser).values(
        'Institute__instt_code', 'Program__program_code', 'event', 'event_date', 'end_date', 'remarks').order_by('event_date')

    print("insttUserList")
    print(insttUserList)


    print("impDatesUserList")
    print(impDatesUserList)
    
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
    progList = InstitutePrograms.objects.values('Program__description').filter(
        Q(Institute__InstituteType_id = "IIT")| Q(Institute__InstituteType_id = "NIT") 
        ).values('Program__description')
        
    progList = progList.distinct().order_by('Program__description') 

        
    insttList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
        Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
        ).values('Institute__instt_name')
    
    insttList = insttList.distinct().order_by('Institute__instt_name')
    
    stateList = InstitutePrograms.objects.values('Institute__state').filter(
        Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
        ).values('Institute__state').distinct().order_by('Institute__state')

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
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values(
        'Institute__instt_name',  'Institute__InstituteType').distinct().order_by('Institute__instt_name')
    
    return render(request, 'NextSteps/seat_chances_assessment.html', 
            {'programUserList':programUserList, 'insttUserList':insttUserList,
            'countryUserList':countryUserList, 'disciplineUserList':disciplineUserList,
            'levelUserList':levelUserList, 'progList':progList, 
            'insttList':insttList, 'stateList':stateList  })
    
    
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
    #button = request.POST.get('submitbuttonMAIN', 'BLANK')
    #button1 = request.POST.get("submitbuttonADV", 'BLANK')

    # Get the student Category
    userid = User.objects.filter(username = request.user).values('id')
    stuUserCat = StudentCategoryUserPref.objects.filter(User_id__in = userid)
 
    category = ''
    for c in stuUserCat:
        category = c.StudentCategory_id
    
    stuCat = StudentCategory.objects.filter(category = category)
    
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
        results = InstituteJEERanks.objects.filter( 
            Q( closing_rank__gte = rankFrom ) | Q( opening_rank__gte = rankFrom )).exclude(
            Institute__InstituteType_id = 'IIT').values('Discipline_id', 'Level_id',
            'Program_id', 'Institute__instt_name', 'Institute_id', 'Institute__state', 'year', 'opening_rank', 
            'closing_rank', 'quota').order_by('Program_id', 'closing_rank')
    
    if rankType == 'ADV':
        results = InstituteJEERanks.objects.filter( 
            (Q( closing_rank__gte = rankFrom ) | Q( opening_rank__gte = rankFrom )), Institute__InstituteType_id = 'IIT').values(
            'Discipline_id', 'Level_id', 'Program_id', 'Institute_id', 
            'Institute__instt_name', 'Institute__state', 'year', 'opening_rank', 
            'closing_rank', 'quota').order_by('Program_id', 'closing_rank')

    if len(progVals) > 0 :
        results = results.filter(Program__description__in=progVals ).order_by('Program_id', 'closing_rank')

    if len(insttVals) > 0 :
        results = results.filter(Institute__instt_name__in=insttVals ).order_by('Program_id', 'closing_rank')

    if stuCat.exists():
        results = results.filter(StudentCategory_id__in=stuCat).order_by('Program_id', 'closing_rank')
    
    err = False

    if results == [] :
        err = True
        results = InstituteJEERanks.objects.filter(Institute__instt_name__in=insttVals).order_by('Program_id', 'closing_rank')


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
            resultSet.append(this)
    
    resultCnt = len(resultSet)
             
    return render(request, 'NextSteps/ifThenAnalysisResults.html', 
            {'resultSet':resultSet, 'err':err,'rankFrom':rankFrom, 
             'rankTo':rankTo, 'progs':progVals, 'instts':insttVals,
             'rankType':rankType, 'resultCnt':resultCnt, 'homestate':homestate})     
    
 
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
        progList = InsttUserPref.objects.filter(
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
        progList = InsttUserPref.objects.exclude(
                Institute__InstituteType_id = "IIT").filter(
                Institute__jee_flag = 'Y').values('Program__description')

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
        progList = InstitutePrograms.objects.filter(
            Institute__InstituteType_id = "IIT").values('Program__description').distinct().order_by('Program__description') 


        # Get the overall Institutes and then apply filters
        insttList = Institute.objects.filter(
            InstituteType_id = "IIT").values('instt_name').distinct().order_by('instt_name')
        
    else:
        # Get the overall Programs and then apply filters
        progList = InstitutePrograms.objects.exclude(
            Institute__InstituteType_id = "IIT").filter(
                Institute__jee_flag = 'Y').values('Program__description').distinct().order_by('Program__description') 
    
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

        
    insttProgList = InstitutePrograms.objects.values('Institute__instt_name', 'Institute__InstituteType').filter(
        Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
        ).values('Institute__instt_name')
    
    insttProgList = insttProgList.distinct().order_by('Institute__instt_name')
    
    stateList = InstitutePrograms.objects.values('Institute__state').filter(
        Q( Institute__InstituteType_id = "IIT") | Q(Institute__InstituteType_id = "NIT")
        ).values('Institute__state').distinct().order_by('Institute__state')

    if countryList.exists() :
        progList = progList.filter(Country__in=countryList).values('Program__description').distinct().order_by('Program__description')
        insttProgList = insttProgList.filter(Country__in=countryList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')
                
    if disciplineList.exists() :
        progList = progList.filter(Discipline__in=disciplineList).values('Program__description').distinct().order_by('Program__description')
        insttProgList = insttProgList.filter(Discipline__in=disciplineList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')

    if levelList.exists() :
        progList = progList.filter(Level__in=levelList).values('Program__description').distinct().order_by('Program__description')
        insttProgList = insttProgList.filter(Level__in=levelList).values('Institute__instt_name',  
                            'Institute__InstituteType').distinct().order_by('Institute__instt_name')


    # Get the current USER program and institute preferences
    programUserList = ProgramUserPref.objects.filter(User__in=userid).values(
        'Program__description').distinct().order_by('Program__description')
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values(
        'Institute__instt_name',  'Institute__InstituteType').distinct().order_by('Institute__instt_name')
    
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
        results = InstituteJEERanks.objects.exclude(
            Institute__InstituteType_id = 'IIT').values('Discipline_id', 'Level_id',
            'Program_id', 'year', 'Institute__instt_name', 'Institute_id', 'Institute__state', 'opening_rank', 
            'closing_rank', 'quota','StudentCategory_id').order_by('Program_id', 'StudentCategory_id', 'year', 'Institute_id', 'closing_rank')
    
    if rankType == 'ADV':
        results = InstituteJEERanks.objects.filter( 
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
        

def userAppDetailsConfirm(request):
    
    return render(request, 'NextSteps/userAppConfirm.html')

def toDoList(request):
    
    return render(request, 'NextSteps/to_do_list.html')

