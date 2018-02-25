from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from NextSteps.forms import SignUpForm
from datetime import datetime
from django.http import JsonResponse

from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import InstitutePrograms, InstituteProgramSeats
from NextSteps.models import Country, Discipline, Level, Program
from NextSteps.models import InstituteJEERanks, InstituteCutOffs, InstituteSurveyRanking
from NextSteps.models import StudentCategory


from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
            'disciplineList': disciplineList, 'levelList':levelList})

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
        insttList = Institute.objects.filter(state__in=stateVals).values()
        print("case 1")
        
        #'instt_id', 'instt_name', 'address_1', 'address_2', 'address_3', 'city', 'pin_code', 'country', 'email_id', 'website', 'InstituteType__description'
        
    # Case 2
    if stateFlag and cityFlag and not typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            city__in=cityVals).values()
        print("case 2")
    
    # Case 3                
    if not stateFlag and cityFlag and not typeFlag:
        insttList = Institute.objects.filter(city__in=cityVals).values()

        print("case 3")

    # Case 4
    if not stateFlag and not cityFlag and not typeFlag:
        insttList = Institute.objects.values()
        print("case 4")

    # Case 5
    if stateFlag and not cityFlag and typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            InstituteType_id__in=insttType).values()
        print("case 5")

    # Case 6
    if stateFlag and cityFlag and typeFlag:
        insttList = Institute.objects.filter(state__in=stateVals).filter(
            city__in=cityVals).filter(InstituteType_id__in=insttType).values()

        print("case 6")

    # Case 7
    if not stateFlag and cityFlag and typeFlag:
        insttList = Institute.objects.filter(city__in=cityVals).filter(
            InstituteType_id__in=insttType).values()

        print("case 7")

    # Case 8
    if not stateFlag and not cityFlag and typeFlag:
        insttList = Institute.objects.filter(
            InstituteType_id__in=insttType).values()
        print("case 8")
    
    # Order the Queryset
    insttListAll = insttList.order_by('state', 'city', 'instt_name')
      
    insttCount = len(insttListAll)
      
    # Get the Institute ids to get the respective rankings 
    insttIds = insttList.values('instt_code')
    
    # get Institute Rankings
    currentYear = str(datetime.now().year)
    insttRanking = InstituteSurveyRanking.objects.filter(year=currentYear).filter(Institute_id__in=insttIds).values()


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
def JEEOpeningClosingRanks(request):

    if request.method == 'POST':    
        request.session['jee-rank-post'] = request.POST
    else:
        if 'jee-rank-post' in request.session:
            request.POST = request.session['jee-rank-post']
            request.method = 'POST'        

    
    switch2015 = request.POST.get('Switch2015', 'off')
    switch2016 = request.POST.get('Switch2016', 'off')
    switch2017 = request.POST.get('Switch2017', 'off')
    switchIIT = request.POST.get('SwitchIIT', 'off')
    switchNIT = request.POST.get('SwitchNIT', 'off')
    
    years = []
    insttType = []
    if switch2015 == 'on':
        years.append('2015')
    if switch2016 == 'on':
        years.append('2016')
    if switch2017 == 'on':
        years.append('2017')
    if switchIIT == 'on':
        insttType.append('IIT')
    if switchNIT == 'on':
        insttType.append('NIT')

    insttList = InstituteJEERanks.objects.filter(year__in=years, Institute__InstituteType__in=insttType).values(
        'year', 'Institute__instt_name', 'Institute__city', 'Program_id', 'quota', 'opening_rank',
        'closing_rank').order_by('year', 'Program_id', 'closing_rank' )

    insttcount = len(insttList)


    page = request.GET.get('page', 1)
    paginator = Paginator(insttList, 15)
    
    try:
        insttList = paginator.page(page)
    except PageNotAnInteger:
        insttList = paginator.page(1)
    except EmptyPage:
        insttList = paginator.page(paginator.num_pages)
    

    
    return render(request, 'NextSteps/JEERanks.html', {
        "insttList" : insttList, 'insttcount':insttcount})

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
    
    insttList = InstituteSurveyRanking.objects.filter().values(
        'year', 'Institute__instt_name', 'Institute__city', 'Discipline_id',
        'rank').order_by('year', 'rank')

    return render(request, 'NextSteps/instt_ranking_filter.html',{
        'insttList':insttList})
    
    
@login_required    
def programFilter(request):
        
    # Get all records to be displayed 
    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
#    programList = Program.objects.all().order_by('description')
    levelList = Level.objects.all()
    
 
    return render(request, 'NextSteps/program_filter.html', {
        'countryList': countryList, 'disciplineList':disciplineList, 
        'levelList':levelList, })

@login_required
def searchProgram (request):
    
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

    # Get the list of institutes based on the user selected programs
    insttList = InstitutePrograms.objects.filter(Program_id__in=programVals).values(
        'Country_id', 'Discipline_id', 'Level_id',
        'Institute__instt_name', 'Institute__address_1', 'Institute__address_2',
        'Institute__address_3', 'Institute__city', 'Institute__state', 'Institute__Country_id',
        'Institute__pin_code', 'Institute__phone_number', 'Institute__email_id',
        'Institute__website', 'Institute__InstituteType', 'Institute__instt_code',
        'Institute__InstituteType__description').distinct()
    
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

    
       