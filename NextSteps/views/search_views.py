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

from NextSteps.decorators import subscription_active

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict

from .common_views import *

@login_required
def SearchFilter(request):

#    fPath = request.get_full_path()
    
#    useview='Blank'

#    if  fPath == "/NextSteps/SearchFilter":
#        useview = 'Search_Instts'
    
#    if fPath == "/NextSteps/SearchFilterRankCutoff":
#        useview = 'Search_Instts_Rank_Cutoff'

#    print("URL===>" + useview)


    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    levelList = Level.objects.all()
    instt_StateList = Institute.objects.values('state').distinct().order_by('state')
    instt_CityList = Institute.objects.values('city').distinct().order_by('city') 
    instt_typeList = InstituteType.objects.values('description').order_by('description')
    
    return render(request, 'NextSteps/search_filter.html', { 
            'instt_StateList' : instt_StateList, 'instt_CityList' : instt_CityList, 
            'instt_typeList' : instt_typeList, 'countryList':countryList,
            'disciplineList': disciplineList, 'levelList':levelList })

@login_required
def InsttList(request):

    '''
    if request.method == 'POST':
        request.session['instts-details-post'] = request.POST
        
        request.session['country-list'] = request.POST.getlist('countryList', [])        
        request.session['discipline-list'] = request.POST.getlist('disciplineList', [])        
        request.session['level-list'] = request.POST.getlist('levelList', [])        
        request.session['state-list'] = request.POST.getlist('stateList', [])        
        request.session['city-list'] = request.POST.getlist('cityList', [])        
        request.session['insttType-list'] = request.POST.getlist('insttTypeList', [])        
        request.session['insttRankYr-list'] = request.POST.getlist('insttRankYrList', [])        
        request.session['insttRankRange-list'] = request.POST.getlist('insttRankRange', [])        
        request.session['program-list'] = request.POST.getlist('programList', [])        
        
        countryVals = request.POST.getlist('countryList', [])
        disciplineVals = request.POST.getlist('disciplineList', [])
        levelVals = request.POST.getlist('levelList', [])
        stateVals = request.POST.getlist('stateList', [])
        cityVals = request.POST.getlist('cityList', [])
        insttTypeVals = request.POST.getlist('insttTypeList', [])
        insttRankYrVals = request.POST.getlist('insttRankYrList', [])
        insttRankRangeVals = request.POST.getlist('insttRankRange', [])
        programVals  = request.POST.getlist('programList', [])
    
        
    else:
        if 'country-list' in request.session:
            countryVals = request.session['country-list']
        else:
            countryVals = []
        
        if 'discipline-list' in request.session:
            disciplineVals = request.session['discipline-list']
        else:
            disciplineVals = []

        if 'level-list' in request.session:
            levelVals = request.session['level-list']
        else:
            levelVals = []

        if 'state-list' in request.session:
            stateVals = request.session['state-list']
        else:
            stateVals = []

        if 'city-list' in request.session:
            cityVals = request.session['city-list']
        else:
            cityVals = []

        if 'insttType-list' in request.session:
            insttTypeVals = request.session['insttType-list']
        else:
            insttTypeVals = []

        if 'insttRankYr-list' in request.session:
            insttRankYrVals= request.session['insttRankYr-list']
        else:
            insttRankYrVals = []
            
        if 'insttRankRange' in request.session:
            insttRankRangeVals = request.session['insttRankRange']
        else:
            insttRankRangeVals = []

        if 'program-list' in request.session:
            programVals = request.session['program-list']
        else:
            programVals = []


        request.method = 'POST'        
    '''    

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
    
    # Whether the user is subscribed
    isSubscribed = isSubsActive(request)
    
#    return render(request, 'NextSteps/instts_search_results.html',{})
    return render(request, 'NextSteps/institute_list.html', {    
        'insttList':insttList,'insttRanking':insttRanking, 'insttCount':insttCount,
        'stateVals':stateVals, 'cityVals':cityVals, 'insttTypeVals':insttTypeVals, 
        'insttRankYrVals':insttRankYrVals, 'programVals':programVals,
        'countryList':countryVals, 'disciplineList': disciplineVals, 
        'levelList':levelVals, 'isSubscribed' : isSubscribed })
    
    
    
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

    print(ranking_years)
    
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



@login_required
def SearchInstts(request):

    if request.method == 'POST':    
        request.session['search-instts-post'] = request.POST
    else:
        if 'search-instts-post' in request.session:
            request.POST = request.session['search-instts-post']
            request.method = 'POST'        
        
    stateVals = request.POST.get('StateValues', '').split(",")
    cityVals = request.POST.get('CityValues', '').split(",")
    typeVals = request.POST.get('TypeValues', '').split(",")


    # Let's get the codes for the selected institute types (we need codes instead of user selected description)
    insttType = InstituteType.objects.filter(description__in=typeVals).values('instt_type_cd')    


    # Set flags to know if user selected state, city and type
    if not insttType:
        typeFlag = False
    else:
        typeFlag = True    
    
    if stateVals == ['']:
        stateFlag = False
    else:
        stateFlag = True    
        
    if cityVals == ['']:
        cityFlag = False
    else:
        cityFlag = True    

    # Get the list of institutes based on the user selected states, cities and institute types. There can 8 combinations, so 8 cases to handle..
    # Case 1
    if stateFlag and not cityFlag and not typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')
        
    # Case 2
    if stateFlag and cityFlag and not typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            city__in=cityVals).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')
    
    # Case 3                
    if not stateFlag and cityFlag and not typeFlag:
        insttList = Institute.objects.filter(city__in=cityVals).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')

    # Case 4
    if not stateFlag and not cityFlag and not typeFlag:
        insttList = Institute.objects.values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')

    # Case 5
    if stateFlag and not cityFlag and typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            InstituteType_id__in=insttType).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')

    # Case 6
    if stateFlag and cityFlag and typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            city__in=cityVals).filter(InstituteType_id__in=insttType).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')

    # Case 7
    if not stateFlag and cityFlag and typeFlag:
        insttList = Institute.objects.filter(city__in=cityVals).filter(
            InstituteType_id__in=insttType).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')

    # Case 8
    if not stateFlag and not cityFlag and typeFlag:
        insttList = Institute.objects.filter(
            InstituteType_id__in=insttType).values('instt_code', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 'pin_code', 'Country', 'phone_number', 'email_id', 'website', 'InstituteType__description')
    
    # Order the Queryset
    insttListAll = insttList.order_by('state', 'city', 'instt_name')
      
    insttCount = len(insttListAll)
      
    # Get the Institute ids to get the respective rankings 
    insttIds = insttList.values('instt_code')

    
    #Get the latest year from Institute Ranking table
    rankyear = InstituteSurveyRanking.objects.all().aggregate(Max('year'))
    surveyyear = rankyear['year__max']
    #currentYear = str(datetime.now().year)
    
    # get Institute Rankings
    insttRanking = InstituteSurveyRanking.objects.filter(year=surveyyear).filter(Institute_id__in=insttIds).values()

    page = request.GET.get('page', 1)
    paginator = Paginator(insttListAll, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    
    return render(request, 'NextSteps/instts_search_results.html', {
        'insttList':insttList,'insttRanking':insttRanking, 'insttCount':insttCount})



@login_required
def ProgramSeatQuotaDetails(request):
    
    # Get the institute names from the request
    insttNames = request.POST.get('selectedInstts', 'Blank').split(";")

    # Remove the empty items from the list. Due to the code in HTML. 
    # The instt names list comes with a ";" at the end and results into an empty
    # item in the list because of split("";) used above to parse names.    
    insttNames = [x for x in insttNames if x != '']

    # Now, let pop (extract) the first item in the list above. HTML is sending 
    # which option user selected as the first item in the list.
    usrSel = request.POST.get('optradio', 'Blank')

    # Set the URL based on the user selection
    if usrSel == "ProgramsAnd Seats":
        nexturl = 'NextSteps/institute_programs_seats.html'
    if usrSel == "ImportantDates":
        nexturl = '#'
    if usrSel == "AdmissionRoutes":
        nexturl = '#'
    if usrSel == "SurveyDetails":
        nexturl = '#'
    
    # Get the institute IDs for those names. the order by is important for the logic to work.
    insttList = Institute.objects.filter(instt_name__in = insttNames).order_by('instt_code')

     # Get the programs for given institutes by disciplines 
#    insttProg = InstitutePrograms.objects.filter(Institute_id__in=insttList, 
#            Discipline = discipline_pref)    #.values('Institute__instt_id', 'Program_id', 'program_duration') 

#    quotaAndSeats = InstituteProgramSeats.objects.filter(
#        Institute_id__in=insttList, Discipline = discipline_pref)
    #.values('Institute__instt_id', 'Program_id', 'SeatQuota_id', 'number_of_seats')
    
    # Create a list that will contain the vales to be sent to HTML for rendering
    num_seats = []
    thisItem = []
    for inst in insttList:

        progList =  InstitutePrograms.objects.filter(
            Institute_id=inst.instt_code).order_by(
                'Institute_id', 'Program_id')

        progCnt = len(progList)

        if progCnt == 0:
            thisItem = [inst.instt_name, 'N/A', 'N/A', 'N/A']
            # Append at the level where all there are no progs and seat are found, 
            # as it will not go into loop for prog and hence seat
            num_seats.append(thisItem)
            
        for prog in progList:

            seatList = InstituteProgramSeats.objects.filter(
                Institute_id=inst.instt_code, Program_id = prog.Program_id).order_by(
                'Institute_id', 'Program_id')                    

            seatCnt = len(seatList)
            
            if seatCnt == 0:
                thisItem = [inst.instt_name, prog.Program_id, 'N/A', 'N/A']
                # Append at the level where all there are no seat are found, 
                # as it will not go into loop for seats
                num_seats.append(thisItem)
            
            for seat in seatList:
                
                if seat.Institute_id == inst.instt_code and prog.Program_id == seat.Program_id : 
                    thisItem = [inst.instt_name, prog.Program_id, seat.SeatQuota_id, seat.number_of_seats] 

                # Append at the level where all the instt, prog and seat are found
                num_seats.append(thisItem)

    # This line to be removed when other pages are ready============================================    
    nexturl = 'NextSteps/institute_programs_seats.html'
    

    return render(request, nexturl, {"num_seats" : num_seats})








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
def instituteTypeSearchFilter(request):
    

    insttTypeList = Institute.objects.values('InstituteType_id', 'InstituteType__description').distinct().order_by('InstituteType_id')

    
    return render(request, 'NextSteps/instt_type_filter.html', {"insttTypeList" : insttTypeList})

@login_required
def instituteTypeSearchResults(request):
    
    if request.method == 'POST':    
        request.session['instt-type-post'] = request.POST
    else:
        if 'instt-type-post' in request.session:
            request.POST = request.session['instt-type-post']
            request.method = 'POST'        
        
    
    insttTypeList = Institute.objects.values('InstituteType_id', 'InstituteType__description').distinct().order_by('InstituteType_id')

    fLoop = True
    filter = []
    for typeLst in insttTypeList:
        txt = typeLst['InstituteType_id']
        onOff = request.POST.get( txt, 'off')
        if onOff.upper() == 'ON':
                filter.append(txt)
        
    insttList = Institute.objects.filter(InstituteType_id__in=filter).values(
        'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'state', 
        'Country_id','pin_code', 'phone_number', 'email_id','website', 
        'InstituteType__description').order_by('Country','state','city')
    
    
    insttcount = len(insttList)

    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    

            
    return render(request, 'NextSteps/instt_type_search_results.html', {
        "insttList" : insttList, 'insttcount':insttcount})


@login_required
def JEERanksFilter(request):
    
    
    return render(request, 'NextSteps/JEERanksFilter.html',{})


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
def insttCutOffFilter(request):
    return render(request, 'NextSteps/insttCutOffFilter.html',{})
    

@login_required
def insttCutOff(request):
    
    if request.method == 'POST':    
        request.session['instt-cutoff-post'] = request.POST
    else:
        if 'instt-cutoff-post' in request.session:
            request.POST = request.session['instt-cutoff-post']
            request.method = 'POST'        


    switch2015 = request.POST.get('Switch2015', 'off')
    switch2016 = request.POST.get('Switch2016', 'off')
    switch2017 = request.POST.get('Switch2017', 'off')
    
    years = []
    insttType = []
    if switch2015 == 'on':
        years.append('2015')
    if switch2016 == 'on':
        years.append('2016')
    if switch2017 == 'on':
        years.append('2017')


    insttList = InstituteCutOffs.objects.filter(year__in=years).values(
        'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'cutOff').order_by(
            'year', 'Program_id' )

    insttcount = len(insttList)

    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    return render(request, 'NextSteps/insttCutOff.html', {
        "insttList" : insttList, 'insttcount':insttcount})


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
    
    
@login_required    
def programFilter(request):
        
    # Get all records to be displayed 
    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    programList = Program.objects.all().order_by('program_code')
    levelList = Level.objects.all()
    
 
    #return render(request, 'NextSteps/program_filter.html', {
    #    'countryList': countryList, 'disciplineList':disciplineList, 
    #    'levelList':levelList, programList})

    return render(request, 'NextSteps/program_search.html', {
        'countryList': countryList, 'disciplineList':disciplineList, 
        'levelList':levelList, 'programList':programList})


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
def seatQuotaFilter(request):
        
    # Get all records to be displayed 
    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    levelList = Level.objects.all()
    quotaList = InstituteProgramSeats.objects.values("StudentCategory__description").distinct()

 
    return render(request, 'NextSteps/seat_quota_filter.html', {
        'countryList': countryList, 'disciplineList':disciplineList, 
        'levelList':levelList, 'quotaList':quotaList})

@login_required
def searchSeatQuota(request):
    
    if request.method == 'POST':    
        request.session['search-instts-post'] = request.POST
    else:
        if 'search-instts-post' in request.session:
            request.POST = request.session['search-instts-post']
            request.method = 'POST'        
        
    countryVals = request.POST.get('CountryValues', '').split(";")
    disciplineVals = request.POST.get('DisciplineValues', '').split(";")
    levelVals = request.POST.get('LevelValues', '').split(";")
    programVals = request.POST.get('ProgramValues', '').split(";")
    seatquotaVals = request.POST.get('SeatQuotaValues', '').split(";")

    # Set flags to know if user selected country, discipline and level
    if countryVals == ['']:
        countryFlag = False
    else:
        countryFlag = True    
    if disciplineVals == ['']:
        disciplineFlag = False
    else:
        disciplineFlag = True    
    if levelVals == ['']:
        levelFlag = False
    else:
        levelFlag = True    
    if programVals == ['']:
        programFlag = False
    else:
        programFlag = True    
    if seatquotaVals == ['']:
        seatquotaFlag = False
    else:
        seatquotaFlag = True    

    # Get the list of institutes based on the user selected programs
    insttList = InstituteProgramSeats.objects.filter(Program_id__in=programVals).values(
        'Country_id', 'Discipline_id', 'Level_id',
        'Institute__instt_name', 'Institute__address_1', 'Institute__address_2',
        'Institute__address_3', 'Institute__city', 'Institute__state', 'Institute__Country_id',
        'Institute__pin_code', 'Institute__phone_number', 'Institute__email_id',
        'Institute__website', 'Institute__InstituteType', 'Institute__instt_code',
        'Institute__InstituteType__description', 'Program_id', 'StudentCategory__description',
        'quota', 'number_of_seats').distinct()
    
    # Case 1
    if countryFlag :
        countryIds = Country.objects.filter(country_name__in=countryVals)
        insttList = insttList.filter(Country_id__in=countryIds)
    if disciplineFlag:
        disciplineIds = Discipline.objects.filter(description__in=disciplineVals)
        insttList = insttList.filter(Discipline_id__in=disciplineIds) 
    if levelFlag:
        levelIds = Level.objects.filter(level_name__in=levelVals)
        insttList = insttList.filter(Level_id__in=levelIds)
    if programFlag:
        programIds = Program.objects.filter(description__in=programVals)
        insttList = insttList.filter(Program_id__in=programIds)
    if seatquotaFlag:
        seatquotaIds = StudentCategory.objects.filter(description__in=seatquotaVals)
        insttList = insttList.filter(StudentCategory_id__in=seatquotaIds)
    

    # Order the Queryset
    insttList = insttList.order_by('Institute__state', 'Institute__city', 'Institute__instt_name')
    insttcount = len(insttList)
      
    insttIds = insttList.values('Institute__instt_code')
      
    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    
    return render(request, 'NextSteps/seatquota_search_results.html', {
        'insttList':insttList,'programVals':programVals, 'seatquotaVals':seatquotaVals,
        'insttcount':insttcount})


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
    stateCityList = list(Institute.objects.filter(instt_code__in = insttIds).values(
        'state', 'city').distinct().order_by('state'))
    
    return JsonResponse(stateCityList, safe=False)
    
    

