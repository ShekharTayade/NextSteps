from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error

import datetime
import time
from django.utils import timezone
from time import gmtime, strftime
from django.contrib import messages
from datetime import datetime

from django.template.context_processors import request
from django.db.models import Max, Min, F, Sum


from NextSteps.decorators import subscription_active

from NextSteps.forms import SignUpForm, UserProfileForm, ContactUsForm, ReferNextStepsForm
from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import Country, Discipline, Level, Program, InstitutePrograms
from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref
from NextSteps.models import ProgramUserPref, InsttUserPref, PromotionCode
from NextSteps.models import UserAccount, UserProfile, Partner_promo
from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import InstitutePrograms, InstituteProgramSeats
from NextSteps.models import Country, Discipline, Level, Program
from NextSteps.models import InstituteSurveyRanking
from NextSteps.models import StudentCategory, EntranceExam


from .common_views import *



def index(request):

    SUBS_MENU = "SHOW_NOSUBS"
    activeSubs = False
    subsExpired = False

    #regPending = False
    au = request.user.is_authenticated

    if au:
        activeSubs = isSubsActive(request)
        subsExpired = isSubsExpired(request)
    
        if activeSubs:
            SUBS_MENU = "SHOW_NOSUBS"
        else:
            if subsExpired:
                SUBS_MENU = "SHOW_RENEWSUBS"
            else:
                SUBS_MENU = "SHOW_SUBS"
            
    url = 'NextSteps/NextSteps_base_vj.html'
        
    if au == False: 
        #response = render(request, 'NextSteps/NextSteps_base.html', {'REG_MENU':REG_MENU,
        #            'SUBS_MENU':SUBS_MENU})
        response = render(request, url, {
                    'SUBS_MENU':SUBS_MENU,
                    'activeSubs' : activeSubs})
    else:
        showReg = request.COOKIES.get('SHOW_REG', '')
        
        if showReg == 'YES' or showReg == '':
            if activeSubs == False:
                response =  render(request, 'NextSteps/checkSubsWithUser.html')
            else:     
                response = render(request, url, {'SUBS_MENU':SUBS_MENU,
                'activeSubs' : activeSubs})
        else:
            response = render(request, url, {'SUBS_MENU':SUBS_MENU, 
            'activeSubs' : activeSubs})
    
    
    return response

'''
def loggedIn_index(request):
    regPending = False
    activeSubs = False

    # Check if it's a registered user
    if isUserRegistered(request):
        regPending = False
        # If user is registered then Check if subscription is active
        if isSubsActive(request):
            activeSubs = True
        else:
            activeSubs = False
    else:
        regPending  = True
        
    if regPending == True:
        REG_MENU = "SHOW_REG_MENU"
        SUBS_MENU = "NOSHOW_SUBS_MENU"
    else:
        if activeSubs:
            SUBS_MENU = "NOSHOW_SUBS_MENU"
            REG_MENU = "NOSHOW_REG_MENU"
        else:
            REG_MENU = "NOSHOW_REG_MENU"
            SUBS_MENU = "SHOW_SUBS_MENU"

    # Get the values for the dropdown filters
    countryList = Country.objects.all()
    disciplineList = Discipline.objects.all()
    levelList = Level.objects.all()
    instt_StateList = Institute.objects.values('state').distinct().order_by('state')
    instt_CityList = Institute.objects.values('city').distinct().order_by('city') 
    instt_typeList = InstituteType.objects.values('description').order_by('description')
    programList = Program.objects.values('description').order_by('description')
    entranceExam = EntranceExam.objects.all()
    rank_range = InstituteSurveyRanking.objects.values('year').distinct().annotate(max_rank = Max('rank'), min_rank = Min('rank'));
    

    response = render(request, 'NextSteps/signedup_user_home.html', {'REG_MENU':REG_MENU,
            'SUBS_MENU':SUBS_MENU,
            'countryList':countryList, 'disciplineList':disciplineList,
            'levelList' :levelList, 'instt_StateList':instt_StateList,
            'instt_CityList':instt_CityList, 'instt_typeList':instt_typeList,
            'programList':programList, 'entranceExam':entranceExam,
            'rank_range':rank_range})

    return response
'''

def NextStepslogin(request):
    
    if request.method == 'POST':
    
        username = request.POST['username'] 
        password = request.POST['password']
        email = request.POST['email']
        
        user = authenticate(request, email=email, username=username, password=password)
       
        if user is not None :
            
            login(request, user)

            if not request.POST.get('remember', None):
                request.session.set_expiry(0)   
                       
            #return redirect('loggedInHome')
            return redirect('index')
        
        else :
            
            return render(request, 'NextSteps/login_allauth.html', {
                'username' : request.user.username, 'invalid' : 'invalid'})
    else:
        return render(request, 'NextSteps/login_allauth.html')



def signup(request):
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        if form.is_valid():
            if userprofile_form.is_valid():

                user = form.save()
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                userprofile = userprofile_form.save(commit=False)
                userprofile.User = user
                userprofile_form.save()
            
                # After successful sign up redirect to payment page
                return redirect('subscription')
    else:
        form = SignUpForm()
        userprofile_form = UserProfileForm()        
#    return render(request, 'NextSteps/signup.html', {'form': form, 'userprofile_form': userprofile_form})
    return render(request, 'NextSteps/SignUpWithProfile.html', {'form': form, 'userprofile_form': userprofile_form})


def checkSubscription(request):
    
    if isSubsActive:
        return redirect('index')
    else:
        return render(request, 'NextSteps/checkSubsWithUser.html')
        

@login_required
def userProfile(request):
    if request.method == 'POST':

        try:
            userid = User.objects.get(username = request.user)
            userObj = UserProfile.objects.get(User = userid)
            form = UserProfileForm(request.POST, instance=userObj)
        except UserProfile.DoesNotExist:
            form = UserProfileForm(request.POST)
            
        if form.is_valid():
            userprofile = form.save(commit=False)
            userprofile.User = request.user
            userprofile.save()
            return redirect('userProfile_Confirm')        
        
    else:
        try:
            userid = User.objects.get(username = request.user)
            userProfileObj = UserProfile.objects.get(User = userid)
            form = UserProfileForm(instance=userProfileObj)                    
        except UserProfile.DoesNotExist:
            form = UserProfileForm(initial={'User': request.user})
        
#    return render(request, 'NextSteps/signup.html', {'form': form, 'userprofile_form': userprofile_form})
    return render(request, 'NextSteps/userProfile.html', {'form': form})
    
    
def userProfileConfirm(request):
    return render(request, 'NextSteps/userProfileConfirm.html')


@login_required
def subscription (request):
    
    if isSubsActive(request):
        username = request.user
        
        # Get logged in user id
        user = getLoggedInUserObject(request)
    
        useraccount = UserAccount.objects.filter(User=user).order_by('-subscription_end_date')
    
        # Get latest subscription end date
        acct = useraccount.order_by('-subscription_end_date')[:1]
    
        subs_end_dt = datetime.datetime.strptime("1900-11-01T01:01:01-0100", "%Y-%m-%dT%H:%M:%S%z")
    
        reg_found = False
    
        for ua in acct:
            subs_end_dt = ua.subscription_end_date
            reg_found = True
    
        subs_end_dt1 = subs_end_dt.strftime("%d-%m-%Y")
        
        if subs_end_dt < timezone.now():
            subs_active = False
        else:
            subs_active = True
    
        return render(request, 'NextSteps/subcription_already_active.html', {'useraccount':useraccount, 
                'reg_found':reg_found, 'subs_end_dt':subs_end_dt, 
                'subs_active': subs_active})
        
    else:
        return render(request, 'NextSteps/subscription.html')

@login_required
def subscriptionStart(request):
    
    # Get logged in user id
    userid = User.objects.filter(username = request.user).values('id')
    user = get_object_or_404(User, username=request.user)
    
    # Get registration, subscription, payment, promotion code details from the request
    regFee = request.POST.get("regFee",0)
    subsFee = request.POST.get("subsFee",0)
    totalFee = request.POST.get("totalFee",0)
    promoCode = request.POST.get("promoCode",'').upper() # always use promo code in CAPS
    percentDisc= request.POST.get("percentDisc",0)
    err_msg = request.POST.get("err_msg",'')
    
    #Get promo code object
    if promoCode != "":
        try:
            promo = PromotionCode.objects.get(promotion_code=promoCode)
            
        except PromotionCode.DoesNotExist:    
            # if user used a non-existent promo code, then let's defaul to "NONE"
            promo = get_object_or_404(PromotionCode, promotion_code='NONE')
            percentDisc = '0'
            
    else:
        # "NONE" promo code is required in DB. If it doesn't exists, then there's a system error.
        promo = get_object_or_404(PromotionCode, promotion_code='NONE')
        percentDisc = '0'
    
    #Get subscription end date
    # Calling add_year method twice as the subsription period is 2 years.
    subs_end = add_year(datetime.datetime.now())
    subs_end = add_year(subs_end)


    #Set default as status PASS and the success message
    pass_fail = 'PASS'      
    msg = 'Registration Complete!'


    try:
        # Save the registration, subscription, payment, promotion code details 
        useracct = UserAccount(User=user, 
                    registration_date = datetime.datetime.now(),
                    subscription_start_date = datetime.datetime.now(), 
                    subscription_end_date = subs_end, 
                    payment_date = datetime.datetime.now(),
                    registration_amount = float(regFee), 
                    subscription_amount = float(subsFee),
                    total_amount = float(totalFee), 
                    PromotionCode = promo,
                    discount_percent = float(percentDisc), 
                    promotion_sys_msg = err_msg )

        useracct.save()

    except Error as e:
        msg = 'Apologies!! Could not process the payment. Please use the contact us link at the bottom of this page to let us know the details and we will help you.'
        pass_fail = 'FAIL'
    
    return render(request, 'NextSteps/payment_confirmation.html', {'save':pass_fail, 
                                        'msg':msg})

    #return render(request, 'NextSteps/subscription_start.html', {'save':pass_fail, 'msg':msg})

@login_required
def renewSubscription(request):
    
    #Get o=logged in userobj
    userObj=getLoggedInUserObject(request)

    # Get current use account details
    useraccount = UserAccount.objects.filter(User=userObj).order_by('-subscription_end_date')
    
    regDate = datetime.time(0, 0, 0)
    validSubscription = False
    for ua in useraccount:
        if ua.subscription_end_date > timezone.now():
            validSubscription=True
        regDate = ua.registration_date

    return render(request, 'NextSteps/renew_subscription.html',{
        'useraccount':useraccount, 'regDate': regDate, 'validSubscription':validSubscription})    

@login_required
def renewSubscriptionConfirm(request):
    
    regFee = 0
    regDate = datetime.time(0, 0, 0)
    subsStartDate = datetime.time(0, 0, 0)
    subsEndDate = datetime.time(0, 0, 0)
    
    # Get subscription code details from the request
    regStr = request.POST.get("regDate",'01/01/1900')
    subsFee = request.POST.get("subsFee",0)
    totalFee = request.POST.get("totalFee",0)
    subsStartStr = request.POST.get("subsStartDate",'01/01/1900')
    subsEndStr= request.POST.get("subsEndDate",'01/01/1900')
    percentDisc= 0
    err_msg = ''

    pass_fail = 'PASS'
    msg = 'Subscription Renewed!'
    
    if regDate == "01/01/1900" or subsStartDate == "01/01/1900" or subsEndDate == "01/01/1900":
        pass_fail = 'FAIL'
        msg = 'Apologies!! Could not process your subscription renewal. Please use the contact us link at the bottom of this page to let us the details and we will help you.'
    else:
        regDate = datetime.datetime.strptime(regStr, "%b. %d, %Y")
        subsStartDate = datetime.datetime.strptime(subsStartStr, "%b. %d, %Y")
        subsEndDate = datetime.datetime.strptime(subsEndStr, "%b. %d, %Y")

    #Get o=logged in userobj
    userObj=getLoggedInUserObject(request)

    # As it's a subscription renewal, so no promo code(i.e. use NONE)!!
    promo = get_object_or_404(PromotionCode, promotion_code='NONE')
    percentDisc = '0'


    try:
        # Save the registration, subscription, payment, promotion code details 
        useracct = UserAccount(User=userObj, 
                    registration_date = regDate,
                    subscription_start_date = subsStartDate, 
                    subscription_end_date = subsEndDate, 
                    payment_date = datetime.datetime.now(),
                    registration_amount = float(regFee), 
                    subscription_amount = float(subsFee),
                    total_amount = float(totalFee), 
                    PromotionCode = promo,
                    discount_percent = float(percentDisc), 
                    promotion_sys_msg = err_msg )
    
        useracct.save()

    except Error as e:
        msg = 'Apologies!! Could not process your subscription renewal. Please use the contact us link at the bottom of this page to let us the details and we will help you.'
        pass_fail = 'FAIL'


    return render(request, 'NextSteps/subscription_start.html', {'save':pass_fail, 'msg':msg})

    

@login_required
def userAccountInformation(request):
    
    username = request.user
    
    # Get logged in user id
    user = getLoggedInUserObject(request)

    useraccount = UserAccount.objects.filter(User=user).order_by('-subscription_end_date')

    # Get latest subscription end date
    acct = useraccount.order_by('-subscription_end_date')[:1]

    subs_end_dt = datetime.datetime.strptime("1900-11-01T01:01:01-0100", "%Y-%m-%dT%H:%M:%S%z")

    reg_found = False

    for ua in acct:
        subs_end_dt = ua.subscription_end_date
        reg_found = True

    subs_end_dt1 = subs_end_dt.strftime("%d-%m-%Y")
    
    

    if subs_end_dt < timezone.now():
        subs_active = False
    else:
        subs_active = True

    return render(request, 'NextSteps/userAccount.html', {'useraccount':useraccount, 
            'reg_found':reg_found, 'subs_end_dt':subs_end_dt, 
            'subs_active': subs_active})


def contactUs(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return redirect('contact_us_confirm')  
    else:
        form = ContactUsForm()
    return render(request, 'contactUs.html', {'form': form})

def contactUsConfirm(request):
    return render(request, 'contactUs_confirm.html')


# Used by Payments page to get the promotion code details. Page makes  an AJAXcall.
def getPromoDetails(request):

    pc = request.GET.get('promoCode', 'Blank')    

    promoCode = PromotionCode.objects.filter(promotion_code = pc.upper())
    
    #No error message
    err_msg= "00"  
    percent = 0.0
    cnt = len(promoCode)

    if cnt == 0:
        #No such promotion code:
        err_msg= "01"  
    else:
        for pc in promoCode:

            if pc.end_date < datetime.date.today():
                # Promotion has expired
                err_msg ="02"  
                
            if pc.start_date > datetime.date.today():
                # Promotion not started yet
                err_msg ="03"  
                
            if err_msg == "00":
                    percent = pc.discount_percent
    
    discount_percent = str(percent)
    promoDetails = [{'discount_percent':discount_percent,'err_msg':err_msg}]
    
    return JsonResponse(promoDetails, safe=False)    


# User Guide Home
def user_guide_pg1(request):
    
        return render(request, 'NextSteps/user_guide_pg1.html')

# Search Feature Overview
def user_guide_pg2(request):
        return render(request, 'NextSteps/user_guide_pg2.html')

# Admission Assistant Feature OVerview        
def user_guide_pg3(request):
        return render(request, 'NextSteps/user_guide_pg3.html')

# Sign up and Subscribe
def user_guide_pg4(request):
        return render(request, 'NextSteps/user_guide_pg4.html')   
    
# Search Feature
def user_guide_pg5(request):
        return render(request, 'NextSteps/user_guide_pg5.html')    

# NextSteps Feature
def user_guide_pg6(request):
        return render(request, 'NextSteps/user_guide_pg6.html') 

# Admission Calendar
def user_guide_adm_calendar(request):
        return render(request, 'NextSteps/user_guide_adm_calendar.html') 

# Study Planner
def user_guide_study_planner(request):
        return render(request, 'NextSteps/user_guide_study_planner.html') 
            
@ login_required
def referNextSteps(request):

    if request.method == 'POST':
        form = ReferNextStepsForm(request.POST)
        if form.is_valid():
            refer = form.save(commit=False)
            refer.referred_by = request.user
            refer.save()            
            return redirect('referNextSteps_confirm')  
    else:
        form = ReferNextStepsForm()
    return render(request, 'NextSteps/referNextSteps.html', {'form': form})

def referNextSteps_confirm(request):
    
    return render(request, 'NextSteps/referNextSteps_confirm.html')

 
def feature_instt_search(request):

    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)

    return render(request, 'NextSteps/feature_instt_search.html',
            {'activeSubs':activeSubs, 'regUser':regUser})
        
    
def feature_important_info(request):
    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)


    return render(request, 'NextSteps/feature_important_info.html',
            {'activeSubs':activeSubs, 'regUser':regUser})
    
       
def feature_calendar(request):
    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)

    return render(request, 'NextSteps/feature_calendar.html',
            {'activeSubs':activeSubs, 'regUser':regUser})


def feature_seat_chances(request):
    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)

    return render(request, 'NextSteps/feature_seat_chances.html',
            {'activeSubs':activeSubs, 'regUser':regUser})


def feature_study_planner(request):
    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)

    return render(request, 'NextSteps/feature_study_planner.html',
            {'activeSubs':activeSubs, 'regUser':regUser})


def feature_application_record(request):
    activeSubs = isSubsActive(request)
    regUser = isUserRegistered(request)

    return render(request, 'NextSteps/feature_application_record.html',
            {'activeSubs':activeSubs, 'regUser':regUser})





@login_required
def partnerAccountInformation(request):
    
    username = request.user

    # Get logged in user id
    user = getLoggedInUserObject(request)
    print (user)

    userpromo = Partner_promo.objects.filter(Partner__User=user).values('PromotionCode')
    print (userpromo)

    # Get details of subscription with the Partner promo code
    subs_details = UserAccount.objects.filter( PromotionCode__in = userpromo  ).annotate(
        amt_withouttax = F('total_amount')  / ( 1 + (18/100) ), 
        partner_fee = ( (F('total_amount')  / ( 1 + (18/100) )) * F('PromotionCode__discount_percent') / 100 )
        ).select_related('User', 'PromotionCode')
    print (subs_details)

    totalFee = subs_details.aggregate( Sum('partner_fee') )
    print(totalFee)
                                         
    return render(request, 'NextSteps/partner_account.html', {'subs_details':subs_details,
                                    'totalFee':totalFee} )

