from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re


def validate_NextSteps_email(value):

    if not "NextSeps.com" in value:
        raise ValidationError(_('The email is invalid. All emails have to be registered on this domain only.'))

def validate_contact_name(value):

    regex = r'^[\w.@+-]+$'
    isValid = re.match(regex, value)
  
    if not isValid:
         raise ValidationError(_('Enter a valid name. It may contain only English letters, '
        'numbers, and @/./+/-/_ characters.'))
     
def validate_image_size(value):
    limit = 50 * 1024
    if value.size > limit:
         raise ValidationError(_('Please upload image with size <= 50KB.'))
        
     