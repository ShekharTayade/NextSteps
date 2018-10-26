from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from NextSteps.forms import SignUpForm
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Max

from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import InstitutePrograms, InstituteProgramSeats
from NextSteps.models import Country, Discipline, Level, Program
from NextSteps.models import InstituteJEERanks, InstituteCutOffs, InstituteSurveyRanking
from NextSteps.models import StudentCategory, EntranceExam, InstituteEntranceExam
from NextSteps.models import InsttUserPref

from NextSteps.decorators import subscription_active

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict

from .common_views import *

# Vijay inserted this below
import json
from django.db.models import Q
import operator
from functools import reduce




def InsttList(request):

    countryVals = request.POST.getlist('countryList', [])
    disciplineVals = request.POST.getlist('disciplineList', [])
    levelVals = request.POST.getlist('levelList', [])
    stateVals = request.POST.getlist('stateList', [])
    cityVals = request.POST.getlist('cityList', [])
    insttTypeVals = request.POST.getlist('insttTypeList', [])
    insttRankYrVals = request.POST.getlist('insttRankYrList', [])
    insttRankRangeVals = request.POST.getlist('insttRankRange', [])
    programVals  = request.POST.getlist('programList', [])
 
    insttList = Institute.objects.values(
        'instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 
        'city', 'state', 'pin_code', 'Country', 'phone_number', 
        'email_id', 'website', 'InstituteType__description')

    # Order the Queryset
    insttList = insttList.order_by('state', 'city', 'instt_name')

    #Apply filters
    if stateVals:
        insttList = insttList.filter(state__in = stateVals)

    if insttTypeVals:
        insttList = insttList.filter(InstituteType__description__in = insttTypeVals)

    if programVals:
        progInstList = InstitutePrograms.objects.filter(Program_id__in = programVals).values('Institute_id')
        insttList = insttList.filter(instt_code__in = progInstList)

    insttCount = len(insttList)
      
    # Get the Institute ids to get the respective rankings 
    insttIds = insttList.values('instt_code')
    
    #Get the latest year from Institute Ranking table
    rankyear = InstituteSurveyRanking.objects.all().aggregate(Max('year'))
    surveyyear = rankyear['year__max']
    #currentYear = str(datetime.now().year)
    
    # get Institute Rankings
    insttRanking = InstituteSurveyRanking.objects.filter(year=surveyyear).filter(Institute_id__in=insttIds).values()

    # Vijay: Include Rank into institute list
    for inst in insttList:
        for rank in insttRanking:
            if rank.get('Institute_id') == inst.get('instt_code'):
                inst.update( {"rank" : rank.get('rank')})
            else:
                inst.update( {"rank" : ""})

    # Vijay: Lookup values for States, Cities and Institute Types
    geostates = list(Institute.objects.values("state").order_by("state").distinct())
    geocities = list(Institute.objects.values("city").order_by("city").distinct())
    instTypes = list(InstituteType.objects.values('description').order_by('description'))
    statecity = list(Institute.objects.filter(instt_code__in = insttIds).values(
        'state', 'city').distinct().order_by('state', 'city'))

    return render(request, 'NextSteps/institute_list.html', {    
        'insttList':insttList,'insttRanking':insttRanking, 'insttCount':insttCount,
        'stateVals':stateVals, 'cityVals':cityVals, 'insttTypeVals':insttTypeVals, 
        'insttRankYrVals':insttRankYrVals, 'programVals':programVals,
        'countryList':countryVals, 'disciplineList': disciplineVals, 
        'levelList':levelVals,'geocities':geocities,'geostates':geostates,
        'instTypes':instTypes, 'statecity':statecity})
    

# Vijay : Method Begin
def InstitueListUnRegistered(request):


    draw = request.GET['draw']
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    order_column = int(request.GET['order[0][column]'])
    # order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
    column = [i.name for n, i in enumerate(Institute._meta.get_fields()) if n == order_column][0]
    global_search = request.GET['search[value]']
    criteria = request.GET.getlist('criteria')
    stateVals = []
    cityVals = []
    insttTypeVals = []

    if criteria:
        criteriaJSON = json.loads(criteria[0])
        stateVals = criteriaJSON['stateList']
        cityVals = criteriaJSON['cityList']
        insttTypeVals = criteriaJSON['insttTypeList']
 
    insttList = Institute.objects.values(
        'instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 
        'city', 'state', 'pin_code', 'Country', 'phone_number', 
        'email_id', 'website', 'InstituteType__description')

    allInstitutes = insttList
    
    #Apply filters
    if global_search:
        query_list = global_search.split()
        insttList = insttList.filter(
            reduce(operator.and_,
                    (Q(instt_name__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                    (Q(address_1__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                    (Q(address_2__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                    (Q(address_3__icontains=q) for q in query_list)) |                    
            reduce(operator.and_,
                    (Q(city__icontains=q) for q in query_list)) |
            reduce(operator.and_,
                    (Q(state__icontains=q) for q in query_list))
        )

    if stateVals:
        insttList = insttList.filter(state__in = stateVals)

    if cityVals:
        insttList = insttList.filter(city__in = cityVals)

    if insttTypeVals:
        insttList = insttList.filter(InstituteType__description__in = insttTypeVals)
    
    '''  
    if global_search:
        insttList = insttList.filter(instt_name__in = global_search)
    '''  
      
    # Get the Institute ids to get the respective rankings 
    insttIds = insttList.values('instt_code')
    
    # Get the latest year from Institute Ranking table
    rankyear = InstituteSurveyRanking.objects.all().aggregate(Max('year'))
    surveyyear = rankyear['year__max']
    
    # Get Institute Rankings
    insttRanking = InstituteSurveyRanking.objects.filter(year=surveyyear).filter(Institute_id__in=insttIds).values()

    objects = []
    for i in insttList.order_by('state','instt_name')[start:start + length]:
        objects.append(i)

    # Vijay: Include Rank into institute list
    '''
    for inst in objects:
        for rank in insttRanking:
            if rank.get('Institute_id') == inst.get('instt_code'):
                inst.update( {"rank" : str(rank.get('rank') )})
            else:
                inst.update( {"rank" : ""})
    '''
    for inst in objects:
        rankedAt = 0
        for rank in insttRanking: 
            if rank.get('Institute_id') == inst.get('instt_code'):
                rankedAt = rank.get('rank')
                break
            else:
                rankedAt = 0
        inst.update({'rank' : rankedAt})


    filtered_count = insttList.count()
    total_count = allInstitutes.count()

    return JsonResponse({
        "sEcho": draw,
        "iTotalRecords": total_count,
        "iTotalDisplayRecords": filtered_count,
        "aaData": objects,
    })

@login_required    
def add_to_preferences(request):
    
    status = "02" # Fail, unless it is save successfully
    instt_code = request.GET.get("instt_code",'')
    
    if instt_code:

        # Get the user object for the logged user
        usr = get_object_or_404(User, username=request.user)
        cnt = get_object_or_404(Country, country_code = "India")
        disc = get_object_or_404(Discipline, discipline_code = "ENGG")
        lvl = get_object_or_404(Level, level_code = "Undergrad")

        instt = get_object_or_404(Institute, instt_code = instt_code)
    
        # check if this institute is already added
        insttPref = InsttUserPref.objects.filter(Institute_id = instt_code)
        
        if insttPref.exists():
            status = "01"   # already added
        else:    
            try:
                pref = InsttUserPref(
                    User = usr,
                    Country = cnt,
                    Discipline = disc,
                    Level = lvl,
                    Program = None,
                    Institute = instt
                )
                
                pref.save()
                status = "00"
            
            except IntegrityError as e:
                status = '02'
        
            except Error as e:
                status = '02'

    return JsonResponse( {"status":status} )
    
@login_required
def instt_all_details(request):

    instt_code = []
    instt_code = request.POST.getlist("instt_code", [])

    # Get basic instt details    
    instt_details = Institute.objects.filter(instt_code__in = instt_code).values(
        'instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 
        'city', 'state', 'pin_code', 'Country', 'phone_number', 
        'email_id', 'website', 'InstituteType_id', 'InstituteType__description')
    
    # Get programs
    progs = InstitutePrograms.objects.filter(Institute_id__in = instt_code).values(
        'Institute_id', 'Program_id')

    # Get survey ranking
    survey_rankings = InstituteSurveyRanking.objects.filter(
        Institute_id__in = instt_code).order_by('Survey_id', 'year')
    
    # Get JEE opening/closing ranks
    jee_ranks = InstituteJEERanks.objects.filter(Institute_id__in = instt_code).order_by(
        'Program_id', 'year', 'StudentCategory_id', 'quota')
    
    # Cut_offs
    cut_offs= InstituteCutOffs.objects.filter(Institute_id__in = instt_code)
    
    # Set Quotas and numbers
    program_seats = InstituteProgramSeats.objects.filter(
        Institute_id__in = instt_code).values('Program_id', 
            'StudentCategory__description', 'quota', "number_of_seats").order_by(
            'Program_id', 'StudentCategory__description', 'quota')
    
    # Entrance Exams
    entrance_exams = InstituteEntranceExam.objects.filter(
        Institute_id__in = instt_code).values('year', 'EntranceExam_id', 'EntranceExam__description')
    
    
    return render(request, 'NextSteps/institute_all_details.html', {    
        'instt_details':instt_details,'progs':progs, 'survey_rankings':survey_rankings,
        'jee_ranks':jee_ranks, 'cut_offs':cut_offs, 'program_seats':program_seats, 
        'entrance_exams':entrance_exams})


@login_required
@subscription_active
def compare_instts(request):

    instt_code = []
    instt_code = request.POST.getlist("selectedInsttCodes", [])

    # Get basic instt details    
    instt_details = Institute.objects.filter(instt_code__in = instt_code).values(
        'instt_code', 'instt_name', 'city', 'state', 
        'InstituteType_id', 'InstituteType__description')
    
    # Get programs
    progs = InstitutePrograms.objects.filter(Institute_id__in = instt_code).values(
        'Institute_id', 'Program_id')

    # Get survey ranking
    survey_rankings = InstituteSurveyRanking.objects.filter(
        Institute_id__in = instt_code).order_by('Survey_id', 'year').order_by(
            'year')
        
    ranking_years =  InstituteSurveyRanking.objects.values(
        'year').distinct().order_by('year')

    
    # Get JEE opening/closing ranks
    jee_ranks = InstituteJEERanks.objects.filter(Institute_id__in = instt_code).order_by(
        'Program_id', 'year', 'StudentCategory_id', 'quota')
    
    # Cut_offs
    cut_offs= InstituteCutOffs.objects.filter(Institute_id__in = instt_code)
    
    # Entrance Exams
    entrance_exams = InstituteEntranceExam.objects.filter(
        Institute_id__in = instt_code).values('year', 'Institute_id', 
            'EntranceExam_id', 'EntranceExam__description')
    
    
    return render(request, 'NextSteps/compare_institutes.html', {    
        'instt_details':instt_details,'progs':progs, 'survey_rankings':survey_rankings,
        'jee_ranks':jee_ranks, 'cut_offs':cut_offs,'entrance_exams':entrance_exams,
        'ranking_years':ranking_years})


# This method returns the cities for the states in JSON.
# this method is used primarily in Search Filter to modify the city list based on the user
# selected states
# The search_filter.html make an AJAX call that get routed here through the url.py 
# and this method returns cities after extracting state list from the response object
def getCitiesforStates(request):

    stateVals = request.GET.get('stateList', 'Blank').split(",")
    
    if stateVals == ['']:
        insttList = list(Institute.objects.values('city').distinct().order_by('city'))
    else:
        insttList = list(Institute.objects.filter(state__in=stateVals).values('city').distinct().order_by('city'))

    return JsonResponse(insttList, safe=False)    


@login_required
def insttRankingFilter(request):
    countryVals = request.POST.getlist('cntList', [])
    disciplineVals = request.POST.getlist('discList', [])
    levelVals = request.POST.getlist('lvlList', [])
    surveyInsttNm = request.POST.get('insttName','')
    
    
    insttList = InstituteSurveyRanking.objects.filter().values(
        'year', 'Institute__instt_name', 'Institute__city', 'Discipline_id',
        'rank').order_by('year', 'rank')
    
    if surveyInsttNm != '':
        insttList = insttList.filter(Institute__instt_name__contains = surveyInsttNm)

    return render(request, 'NextSteps/instt_ranking_filter.html',{
        'insttList':insttList})
            
'''
@login_required
def JEERanksFilter(request):
    
    
    return render(request, 'NextSteps/JEERanksFilter.html',{})
'''

@login_required
def getJeeRankYears(request):

    years = InstituteJEERanks.objects.values('year').distinct()
    
    return JsonResponse(list(years), safe=False)    
    

@login_required
def JEEOpeningClosingRanks(request):

    '''
    if request.method == 'POST':    
        request.session['jee-rank-post'] = request.POST
    else:
        if 'jee-rank-post' in request.session:
            request.POST = request.session['jee-rank-post']
            request.method = 'POST'        
    '''

    switch2015 = request.POST.get('Switch2015', 'off')
    switch2016 = request.POST.get('Switch2016', 'off')
    switch2017 = request.POST.get('Switch2017', 'off')
    switchIIT = request.POST.get('SwitchIIT', 'off')
    switchNIT = request.POST.get('SwitchNIT', 'off')
    
    years = []
    if switch2015 == 'on':
        years.append('2015')
    if switch2016 == 'on':
        years.append('2016')
    if switch2017 == 'on':
        years.append('2017')
        
    if switchIIT == 'on':
        insttType= 'IIT'
    if switchNIT == 'on':
        insttType = 'NON-IIT'
    if switchIIT == 'on' and switchNIT == 'on':
        insttType = 'ALL'
        

    if insttType == "IIT":
        insttList = InstituteJEERanks.objects.filter(year__in=years, Institute__InstituteType=insttType).values(
            'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'opening_rank',
            'closing_rank').order_by('year', 'Program_id', 'closing_rank' )
            
    elif insttType == "NON-IIT":
        insttList = InstituteJEERanks.objects.filter(year__in=years, Institute__jee_flag="Y").exclude(
            Institute__InstituteType="IIT").values(
            'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'opening_rank',
            'closing_rank').order_by('year', 'Program_id', 'closing_rank' )
            
    elif insttType == "ALL":
        insttList = InstituteJEERanks.objects.filter(year__in=years).values(
            'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'opening_rank',
            'closing_rank').order_by('year', 'Program_id', 'closing_rank' )

    '''
    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    '''

    
    return render(request, 'NextSteps/JEERanks.html', {"insttList" : insttList})


@login_required
def JEERanks(request):
    year = request.POST.getlist('year', [])
    rankType = request.POST.getlist('rankType', [])
    
    # Get Insititues
    insttList = InstituteJEERanks.objects.filter(Institute__jee_flag="Y").values(
            'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'opening_rank',
            'closing_rank').order_by('year', 'Program_id', 'closing_rank' )

    if year != []:
        insttList = insttList.filter(year__in = year)


    if rankType != []:
        # If both JEE ADV and MAIN are selected then we don't need to apply any filter
        if len(rankType) <= 1:

            for i in rankType:
                if i == "JEE-ADV":
                    insttList = insttList.filter(Institute__InstituteType = "IIT")
                
                if i == "JEE-MAIN":
                    insttList = insttList.exclude(Institute__InstituteType="IIT")
            
            
    return render(request, 'NextSteps/JEERanks.html', {"insttList" : insttList})
    

@login_required
def searchProgram (request):
    countryVals = request.POST.getlist('cntList', [])
    disciplineVals = request.POST.getlist('discList', [])
    levelVals = request.POST.getlist('lvlList', [])
    programVals  = request.POST.getlist('progList', [])
    insttNameVals  = request.POST.get('insttName', '')


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

    # Get the list of institutes based on the user selected programs
    insttList = InstitutePrograms.objects.filter(Program_id__in=programVals).values(
        'Country_id', 'Discipline_id', 'Level_id',
        'Institute__instt_name', 'Institute__address_1', 'Institute__address_2',
        'Institute__address_3', 'Institute__city', 'Institute__state', 'Institute__Country_id',
        'Institute__pin_code', 'Institute__phone_number', 'Institute__email_id',
        'Institute__website', 'Institute__InstituteType', 'Institute__instt_code',
        'Institute__InstituteType__description').distinct()
    
    # Set other filters
    if countryCodes :
        insttList = insttList.filter(Country_id__in=countryCodes)
    if disciplineCodes:
        insttList = insttList.filter(Discipline_id__in=disciplineCodes) 
    if levelCodes:
        insttList = insttList.filter(Level_id__in=levelCodes)

    if insttNameVals != '':    
        insttList = insttList.filter(Institute__instt_name__contains = insttNameVals)


    # Order the Queryset
    insttList = insttList.order_by('Institute__state', 'Institute__city', 'Institute__instt_name')
    
    
    insttcount = len(insttList)
    '''  
    insttIds = insttList.values('Institute__instt_code')
      
    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    '''
    
    return render(request, 'NextSteps/program_search_results.html', {
        'insttList':insttList,'programVals':programVals, 'insttcount':insttcount})


@login_required
def searchEntranceExams(request):

    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    levelList = Level.objects.all()

    countryVals = request.POST.getlist('cntList', [])
    disciplineVals = request.POST.getlist('discList', [])
    levelVals = request.POST.getlist('lvlList', [])
    exam_levelVals = request.POST.getlist('exam_levels', [])
    examVals = request.POST.get('exam_name', '')

    
    # Hardcoding the filters on country, discipline and Level.  This needs to be
    # removed later on and the front end filter needs to be implemented for user.
    examList = EntranceExam.objects.filter(Country_id = 'India', 
        Discipline_id = 'ENGG', Level_id = 'Undergrad').order_by('entrance_exam_code')

    if examVals != '':
        examList = examList.filter(description__contains = examVals)

    if exam_levelVals != []:
        examList = examList.filter(exam_level__in = exam_levelVals)

    return render(request, 'NextSteps/entrance_exams.html', {
        'countryList':countryList,'disciplineList':disciplineList, 
        'levelList':levelList, 'examList':examList})
    

# Returns all the states and cities for ENGG Discipline
def insttStatesCities(request):

    # Get all institute IDs with ENGG discipline
    insttIds = InstitutePrograms.objects.filter(Discipline_id = "ENGG", 
                Level_id = "Undergrad", Country_id = "India").values(
                'Institute_id').distinct()
    
    # Get States and Cities Objects
    # Vijay : 01-09-2018 , order_by city is added
    stateCityList = list(Institute.objects.filter(instt_code__in = insttIds).values(
        'state', 'city').distinct().order_by('state', 'city'))
    
    return JsonResponse(stateCityList, safe=False)
    
    
def instts_by_entrance_exam_code(request):
    
    examVals = request.GET.getlist('entrance_exam_code', [])
    instt_list = InstituteEntranceExam.objects.filter(EntranceExam_id__in = examVals).values(
        'Institute__instt_name', 'Institute__address_1', 'Institute__address_2',
        'Institute__address_3', 'Institute__city', 'Institute__state', 'Institute__Country_id',
        'Institute__pin_code', 'Institute__phone_number', 'Institute__email_id',
        'Institute__website', 'Institute__InstituteType', 'Institute__instt_code',
        'Institute__InstituteType__description').distinct().order_by('Institute__instt_name')
        
    return render (request, 'NextSteps/instts_by_entrance_exams.html', {'instt_list':instt_list,
                        'entrance_exam_code':examVals})

