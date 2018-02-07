from django.core.exceptions import PermissionDenied
from NextSteps.models import UserAccount

from django.utils import timezone

def subscription_active(function):
    def wrap(request, *args, **kwargs):
        valid_subs = False
        accnt = UserAccount.objects.filter(User__username=request.user)
        
        for acc in accnt:
            # if user has an account but the subscription has expired then this is subscription renewal
            if acc.subscription_end_date > timezone.now():
                valid_subs = True
                break
            else:
                valid_subs = False

            # allow to proceed only if there is no valid subscription
        if valid_subs == True:
            return function(request, *args, **kwargs)
        else :
            raise PermissionDenied
            
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap