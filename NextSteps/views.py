from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from .forms import SignUpForm
from datetime import datetime
from django.http import JsonResponse

from .models import Institute, InstituteType, InstituteSurveyRanking
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'NextSteps/NextSteps.html')


def NextStepslogin(request):

    if request.method == 'POST':
    
        username = request.POST['username'] 
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None :
            login(request, user)
            return redirect('index')
        else :
            return render(request, 'NextSteps/Login.html', {'username' : request.user.username, 'invalid' : 'invalid'})
    else:
        return render(request, 'NextSteps/login.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            # After successful sign up redirect to payment page
            return redirect('payment')
    else:
        form = SignUpForm()
    return render(request, 'NextSteps/signup.html', {'form': form})


def payment (request):
    return render(request, 'NextSteps/payment.html')


def SearchFilter(request):

    fPath = request.get_full_path()
    
    useview='Blank'

    if  fPath == "/NextSteps/SearchFilter":
        useview = 'Search_Instts'
    
    if fPath == "/NextStepsSearchFilterRankCutoff":
        useview = 'Search_Instts_Rank_Cutoff'

    print("URL===>" + useview)

    instt_StateList = Institute.objects.values('state').distinct().order_by('state')
    instt_CityList = Institute.objects.values('city').distinct().order_by('city') 
    instt_typeList = InstituteType.objects.values('description').order_by('description')
    
    return render(request, 'NextSteps/search_filter.html', {'useview' : useview, 'instt_StateList' : instt_StateList, 'instt_CityList' : instt_CityList, 'instt_typeList' : instt_typeList})



def SearchInstts(request):

    stateVals = request.GET.get('StateValues', 'Blank').split(",")
    cityVals = request.GET.get('CityValues', 'Blank').split(",")
    typeVals = request.GET.get('TypeValues', 'Blank').split(",")

    print("TYPE.....")
    print(typeVals)

    # Let's get the codes for the selected institute types (we need codes instead of user selected description)
    insttType = InstituteType.objects.filter(description__in=typeVals).values('instt_type_cd')

    print("TYPE Queryset.....")
    print(insttType)
    

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
      
    # Get the Institute ids to get the respective rankings 
    insttIds = insttList.values('instt_code')
    print("Institute Codes")
    print(insttIds)
    
    # get Institute Rankings
    currentYear = str(datetime.now().year)
    insttRanking = InstituteSurveyRanking.objects.filter(year=currentYear).filter(Institute_id__in=insttIds).values()
    print("Institute Ranking")
    print(insttRanking)

    print("Institutes ")
    print(insttList)

    
    return render(request, 'NextSteps/instts_search_results.html', {
        'insttList':insttList,'insttRanking':insttRanking})



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
    
    # Get the institute IDs for those names. the order by is import for the logic to work.
    insttList = Institute.objects.filter(instt_name__in = insttNames).order_by('instt_code')

     # Get the programs for given institutes by disciplines 
#    insttProg = InstitutePrograms.objects.filter(Institute_id__in=insttList, 
#            Discipline = discipline_pref)    #.values('Institute__instt_id', 'Program_id', 'program_duration') 

#    quotaAndSeats = InstituteProgramSeats.objects.filter(
#        Institute_id__in=insttList, Discipline = discipline_pref)
    #.values('Institute__instt_id', 'Program_id', 'SeatQuota_id', 'number_of_seats')
    
    # Create a Python list that will contain the vales to be sent to HTML for rendering
    num_seats = []
    thisItem = []
    for inst in insttList:
        print(inst.instt_name)

        progList =  InstitutePrograms.objects.filter(
            Institute_id=inst.instt_id, Discipline = discipline_pref).order_by(
                'Institute_id', 'Program_id')

        progCnt = len(progList)

        if progCnt == 0:
            thisItem = [inst.instt_name, 'N/A', 'N/A', 'N/A']
            # Append at the level where all there are no progs and seat are found, 
            # as it will not go into loop for prog and hence seat
            num_seats.append(thisItem)
            
        for prog in progList:

            seatList = InstituteProgramSeats.objects.filter(
                Institute_id=inst.instt_code, Program_id = prog.Program_id, 
                Discipline = discipline_pref).order_by(
                'Institute_id', 'Program_id')                    

            seatCnt = len(seatList)
            
            if seatCnt == 0:
                thisItem = [inst.instt_name, prog.Program_id, 'N/A', 'N/A']
                # Append at the level where all there are no seat are found, 
                # as it will not go into loop for seats
                num_seats.append(thisItem)
            
            for seat in seatList:
                
                print(seat.SeatQuota_id)
                print(seat.number_of_seats)
                    
                if seat.Institute_id == inst.instt_code and prog.Program_id == seat.Program_id and seat.Discipline_id == discipline_pref : 
                    thisItem = [inst.instt_name, prog.Program_id, seat.SeatQuota_id, seat.number_of_seats] 

                # Append at the level where all the instt, prog and seat are found
                num_seats.append(thisItem)

    print("LIST.............")    
    print (num_seats)            
    print (len(num_seats))            
    
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
    
    print(stateVals)
    
    if stateVals == ['']:
        print("IF................")
        insttList = list(Institute.objects.values('city').distinct().order_by('city'))
    else:
        print("ELSE................")
        insttList = list(Institute.objects.filter(state__in=stateVals).values('city').distinct().order_by('city'))

    print(insttList)

    return JsonResponse(insttList, safe=False)    





