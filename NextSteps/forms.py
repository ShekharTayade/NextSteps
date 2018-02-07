from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from NextSteps.models import ContactForm, UserAppDetails
from NextSteps.validators import validate_NextSteps_email, validate_contact_name

from django.core.validators import validate_slug, MinLengthValidator

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ContactUsForm(forms.ModelForm):

    name = forms.CharField( widget=forms.TextInput(
        attrs={'placeholder': 'Please use only letter, numbers. Use your login name in case you are registered.'}
        ),
        validators=[validate_contact_name]
    )

    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder':"Please don't forget the STD code in case entering a landline."}
        ), required=False)

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':2, 'placeholder': 'Write you message here'}
        ),
        max_length=4000,
        help_text='The max length is 4000 characters.')
  
    class Meta:
        model = ContactForm
        fields = ['name', 'email_id', 'phone_number', 'subject', 'message']
        



class UserAppDetailsForm(forms.ModelForm):
    
    class_10th_school_address = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':2, 'placeholder': 'Enter school address'}
        ),
        max_length=3000,
        help_text='The max length is 3000 characters.')
    
    class_12th_school_address = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':2, 'placeholder': 'Enter school/college address'}
        ),
        max_length=3000,
        help_text='The max length is 3000 characters.')
    
    class Meta:
        model = UserAppDetails
        fields = ['User', 'name', 'date_of_birth', 'gender',
                  'mothers_name', 'mothers_qualification',
                  'mothers_occupation', 'mothers_income', 
                  'fathers_name', 'fathers_qualification',
                  'fathers_occupation', 'fathers_income', 
                  'StudentCategory', 'person_with_disability',
                  'percetage_of_disability', 'state_of_eligibility',
                  'nationality', 'address', 'locality',
                  'city_town_village', 'district', 'pin_code',
                  'state', 'Country', 'phone_number', 'email_id',
                  'aadhaar_number', 'class_10th_year_of_passing',
                  'class_10th_percentage_cgpa', 'class_10th_school_address',
                  'class_10th_board_or_university', 'class_12th_year_of_passing',
                  'class_12th_percentage_cgpa', 'class_12th_school_address',
                  'class_12th_board_or_university', 'guardians_name', 
                  'guardians_qualification', 'guardians_occupation', 
                  'guardians_income', 'candidate_photo', 'candidate_signature',
                  'parent_signature'
                  ]
        