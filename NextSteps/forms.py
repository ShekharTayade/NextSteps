from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from NextSteps.models import ContactForm, UserAppDetails, UserProfile, ReferNextSteps
from NextSteps.validators import validate_NextSteps_email, validate_contact_name, validate_image_size

from django.core.validators import validate_slug, MinLengthValidator

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


from string import Template
from django.utils.safestring import mark_safe
from django.forms import ImageField

class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        html =  Template("""<img src="$link"/>""")
        return mark_safe(html.substitute(link=value))

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 
                 'password2')
    #, 'date_of_brith', 'address','city','state',
    #             'education')
        
    # This method is required for 'allauth'
    '''
    def signup(self, request, user):
        
        import pdb
        pdb.set_trace()
        
        
       # Save user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        import pdb
        pdb.set_trace()

        # Save user profile data
        userprofile, created = models.UserProfile.objects.get_or_create(user=user)
        user.userprofile.date_of_birth = self.cleaned_data['date_of_birth']
        user.userprofile.address= self.cleaned_data['address']
        user.userprofile.city = self.cleaned_data['city']
        user.userprofile.state = self.cleaned_data['state']
        user.userprofile.phone_number = self.cleaned_data['phone_number']
        user.userprofile.education = self.cleaned_data['education']
        
        user.userprofile.save()        
    '''
        
class UserProfileForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':2, 'placeholder': 'Enter address'}
        ),
        max_length=2000,
        help_text='The max length is 3000 characters.',
        required=False)

    education = forms.CharField( widget=forms.TextInput(
        attrs={'placeholder': 'Please enter the currently pursuing (ex. X, XI, XII, B.E. etc.)'}
        ),
        required=False
    )

    
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'gender', 'address', 'city', 'state', 'phone_number', 'education')

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
        help_text='The max length is 3000 characters.',
        required=False)
    
    class_12th_school_address = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':2, 'placeholder': 'Enter school/college address'}
        ),
        max_length=3000,
        help_text='The max length is 3000 characters.',
        required=False)
    
    candidate_photo = forms.ImageField(
        validators=[validate_image_size],
        required=False
    )

    class Meta:
        model = UserAppDetails
        fields = ['name', 'date_of_birth', 'gender',
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


class ReferNextStepsForm(forms.ModelForm):

    name = forms.CharField( widget=forms.TextInput(
        attrs={'placeholder': 'Please enter the name of your friend'}
        )
    )

    email_id = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder':"Please enter your friend's email id"}), 
        required=False)
    

    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder':"Please enter your friend's 10 digit mobile number"}
        ), required=False)

    message = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Write a line for your friend'}
        ),
        max_length=2000,
        help_text='The max length is 2000 characters.')
  
    class Meta:
        model = ReferNextSteps
        fields = ['name', 'email_id', 'phone_number', 'message']
        


        