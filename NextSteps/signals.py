from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.shortcuts import redirect

@receiver(user_signed_up)
def showPaymentPage(sender, **kwargs):
    print("Sign Up Signal Captured!!")
    redirect('payment')
    

