from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, DatabaseError, Error

import datetime
from django.utils import timezone

from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref
from NextSteps.models import ProgramUserPref, InsttUserPref, UserAccount


def getLoggedInUserObject(request):

    # Get logged in user id
    userid = User.objects.filter(username = request.user).values('id')
    userObj = get_object_or_404(User, username=request.user)
    
    return userObj

def isUserRegistered(request):

    ret = False
    
    
    try:
        # Get logged in user id
        userObj = User.objects.get(username = request.user)
        # Check in the UserAccount model for registered user
        regUser = UserAccount.objects.filter(User = userObj)
        if regUser.exists():
            ret=True
        else:
            ret=False
    
    except User.DoesNotExist:    
        ret = False
            
    
    return ret

def isSubsActive(request):
    
    ret=False
    
    try:
        # Get logged in user id
        userObj = get_object_or_404(User, username = request.user)
        
        useracct = UserAccount.objects.filter(User = userObj).order_by('subscription_end_date')
        for ua in useracct:
            print(ua.subscription_start_date)
            if ua.subscription_end_date > timezone.now():
                ret=True
                break
        
    except User.DoesNotExist:    
        ret = False

    return ret

# Get user preferences
def getUserPrefs(username, type) :

    type = type.upper()
    ret = []

    if type == 'COUNTRY':
        #Get Countries
        cnty = CountryUserPref.objects.filter(User__username = username)
        ret = cnty
    elif type == 'DISCIPLINE':  
        # Get Disciplines
        disc = DisciplineUserPref.objects.filter(User__username = username)
        ret = disc
    elif type == 'LEVEL':
        # Get Levels
        level = LevelUserPref.objects.filter(User__username = username)
        ret = level
    elif type == 'PROGRAM':
        # Get Programs
        program = ProgramUserPref.objects.filter(User__username = username)
        ret = program
    elif tpye == 'INSTITUTE':
        # Get Institutes
        instt = InsttUserPref.objects.filter(User__username = username)
        ret = instt
    
    return(ret)



# Check if the int given year is a leap year
# return true if leap year or false otherwise
def is_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


THIRTY_DAYS_MONTHS = [4, 6, 9, 11]
THIRTYONE_DAYS_MONTHS = [1, 3, 5, 7, 8, 10, 12]

# Inputs -> month, year Booth integers
# Return the number of days of the given month
def get_month_days(month, year):
    if month in THIRTY_DAYS_MONTHS:   # April, June, September, November
        return 30
    elif month in THIRTYONE_DAYS_MONTHS:   # January, March, May, July, August, October, December
        return 31
    else:   # February
        if is_leap_year(year):
            return 29
        else:
            return 28

# Checks the month of the given date
# Selects the number of days it needs to add one month
# return the date with one month added
def add_month(date):
    current_month_days = get_month_days(date.month, date.year)
    next_month_days = get_month_days(date.month + 1, date.year)

    delta = datetime.timedelta(days=current_month_days)
    if date.day > next_month_days:
        delta = delta - datetime.timedelta(days=(date.day - next_month_days) - 1)

    return date + delta


def add_year(date):
    if is_leap_year(date.year):
        delta = datetime.timedelta(days=366)
    else:
        delta = datetime.timedelta(days=365)

    return date + delta


