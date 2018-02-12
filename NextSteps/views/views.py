from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
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


import pdb

from django.template.context_processors import request

from NextSteps.decorators import subscription_active

from NextSteps.forms import SignUpForm, ContactUsForm
from NextSteps.models import Institute, InstituteType, InstituteSurveyRanking
from NextSteps.models import Country, Discipline, Level, Program, InstitutePrograms
from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref
from NextSteps.models import ProgramUserPref, InsttUserPref, PromotionCode
from NextSteps.models import UserAccount

from .common_views import *

def index(request):

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

    # Clear the earlier messages that may be in the storage
#    storage = messages.get_messages(request)
#    for _ in storage:
#        pass
        
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
            
    response = render(request, 'NextSteps/NextSteps.html', {'REG_MENU':REG_MENU,
                    'SUBS_MENU':SUBS_MENU})
    return response


def NextStepslogin(request):

    if request.method == 'POST':
    
        username = request.POST['username'] 
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None :
            
            login(request, user)

            if not request.POST.get('remember', None):
                request.session.set_expiry(0)   
                       
            return redirect('index')
        
        else :
            
            return render(request, 'NextSteps/login.html', {
                'username' : request.user.username, 'invalid' : 'invalid'})
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



@login_required
#@subscription_active
def payment (request):
    return render(request, 'NextSteps/payment.html')

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
    subs_end = add_year(datetime.datetime.now())

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
        print(e)
        msg = 'Apologies!! Could not process the payment. Please use the contact us link at the bottom of this page to let us the details and we will help you.'
        pass_fail = 'FAIL'


    return render(request, 'NextSteps/subscription_start.html', {'save':pass_fail, 'msg':msg})

@login_required
@subscription_active
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
@subscription_active
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

    print("In coming Dates......")
    print(regStr)
    print(subsStartStr)
    print(subsEndStr)
    
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
        print(e)
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
            'reg_found':reg_found, 'subs_end_dt':subs_end_dt1, 
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
