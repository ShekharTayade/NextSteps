from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db.models.fields import DecimalField

from django.db.models.signals import post_save
from django.dispatch import receiver

from NextSteps.validators import validate_max7days, validate_max100, validate_max24hrs

# Model name - Country
# This model will store all the countries that NextSteps will serve (ex. 
# India, USA, UK, Australia etc.)
class Country(models.Model):
    country_code = models.CharField(max_length=80, primary_key = True) 
    country_name = models.CharField(max_length=100, blank = True, null=True, unique=True)

    def __str__(self):
        return self.country_code

# Model name - Level
# This model will store all the levels that NextSteps will serve (ex. 
# Undergraduation, postgraduation, Pre-university etc.)
# As this will not change frequently, instead of having a model on it's own, 
# it will included as a field on the NextStep_driver model.
class Level(models.Model):
    level_code = models.CharField(max_length=50, primary_key = True) 
    level_name = models.CharField(max_length=100, blank = True, null=True, unique=True)

    def __str__(self):
        return models.Model.__str__(self)


# Model name - Program
# This model will store all the programs under each discipline and level 
# (ex. B.Tech Computer Science, M. Tech Mechanical, B.E. Electrical,
# B. Tech Electronics and Communication, MBBS, BA LLB, BBA, BBM etc.)  
class Program(models.Model):
    program_code = models.CharField(max_length=1000, primary_key = True)
    description = models.CharField(max_length=1000, blank = True, default='')
    degree = models.CharField(max_length=300, blank = True, default='')
    program_group = models.CharField(max_length=300, blank = True, default='')
    
    def __str__(self):
        return models.Model.__str__(self)
    

# Model name - Discipline
# This model will store all the disciplines that NextSteps will serve (ex. 
# Engineering, Medical, Management, Law,
# Science, Art, Commerce, Agriculture, Veterinary, etc.)
class Discipline(models.Model):    
    discipline_code = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=300, blank=True, null=True, unique=True)
    
    def __str__(self):
        return models.Model.__str__(self)
 
 
# Model - InstituteType
# This model stores the type of institute (ex. IIT, NIT, GEC, PEC etc.)
class InstituteType(models.Model):
    instt_type_cd = models.CharField(max_length=8, primary_key=True)
    description = models.CharField(max_length=1000, blank=True, null=True, unique=True)
    
    def __str__(self):
        return models.Model.__str__(self)


# Model - InstituteType
# This model stores the Seat Quotas    
class SeatQuota(models.Model):    
    seat_quota_code = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=1000, blank=True, null=True, unique=True)
    
    def __str__(self):
        return models.Model.__str__(self)


# Model - StudentCategory
# This model stores the birth categories such as General, OBC, ST, ST etc.
class StudentCategory(models.Model):
    category = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=100, blank=True, null=True, unique=True)
    jee_flag = models.CharField(max_length=1, blank=True, default='')

    def __str__(self):
        return self.category


# Model - EntranceExam
# This model stores the Entrance Exam Types        
class EntranceExam(models.Model):    
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    entrance_exam_code = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=2000, blank=True, default='')
    exam_level = models.CharField(max_length=50, blank=True, default='')
    state = models.CharField(max_length=50, blank=True, default='')
    
    def __str__(self):
        return models.Model.__str__(self)

    
class Institute(models.Model):
    instt_code = models.AutoField(primary_key=True)
    instt_name = models.CharField(max_length=500, blank=False, unique=True)
    address_1 = models.CharField(max_length=300, blank=False, null=False)
    address_2 = models.CharField(max_length=300, blank=True, default='')
    address_3 = models.CharField(max_length=300, blank=True, default='')
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    pin_code = models.IntegerField(blank=True, null=True)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    phone_number = models.CharField(max_length=30, blank=True, default='')
    email_id = models.EmailField(blank=True, default='')
    website = models.CharField(max_length=200, blank=True, default='')
    InstituteType = models.ForeignKey(InstituteType, on_delete=models.SET_NULL, 
        blank=True, null=True)
    aicte_id = models.CharField(max_length=20, blank=True, default='')
    abbreviation = models.CharField(max_length=20, blank=True, default='')
    jee_flag = models.CharField(max_length=1, blank=True, default='')

    def __str__(self):
        return models.Model.__str__(self)



# Model - InstitutePrograms
# This model will store the relationship between country, discipline, level,
# programs, and the institutes for each combination of these relationships. 
# This the BASE model that will drive all the searches for users.
# It will have an auto generated primary key
# Model - Institute
# This model stores all the details for the each institute
class InstitutePrograms(models.Model):
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete = models.PROTECT)
    Level = models.ForeignKey(Level, on_delete = models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    program_duration = models.CharField(max_length=30,blank = True, default='')
    Institute  = models.ForeignKey(Institute, on_delete=models.SET_NULL, 
                               blank = True, null = True)

    def __str__(self):
        return models.Model.__str__(self)


    
# Model - InstituteProgramEntrance
# This model stores for each institute and for each discipline, program and 
# level the Entrance exams used by the Institutes
class InstituteProgramEntrance(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    EntranceExam = models.ForeignKey(EntranceExam, on_delete=models.SET_NULL, 
        blank=True, null=True)
     
    def __str__(self):
        return models.Model.__str__(self)


# Model - EntranceExamImpDates
# This model stores the important dates for the Entrance Exams
class EntranceExamImpDates(models.Model):    
    id = models.AutoField(primary_key=True)
    entrance_exam_code = models.CharField(max_length=50)
    year = models.CharField(max_length=4, blank=False)
    event = models.CharField(max_length=500, blank=True, default='')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    remarks= models.CharField(max_length=2000, blank=True, default='')
    
    def __str__(self):
        return self.year    




# Model - InstituteProgramSeats
# This model stores for each institute and for each discipline, program and 
# level the seat quote and the seats available at the Institute.
# "category" field is to be used to store the categories such as GEN, OBC, SC, ST etc.
# "SeatQuota" is to be used for storing quotas such as ""AI", "HS", "OS" etc. 
class InstituteProgramSeats(models.Model):
    
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    quota = models.CharField(max_length=50, blank=True, default='')
    StudentCategory = models.ForeignKey(StudentCategory, on_delete=models.PROTECT, 
        blank=True, null=True)
    number_of_seats = models.IntegerField(blank=True, null=True)
     
    def __str__(self):
        return models.Model.__str__(self)
    
    

class InstituteProgramImpDates(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    event = models.CharField(max_length=500, blank=True, default='')
    event_date = models.DateField(blank=True, null=True)
    event_order = models.IntegerField(blank=True, null=True)
    event_duration_days = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    remarks= models.CharField(max_length=2000, blank=True, default='')
    def __str__(self):
        return models.Model.__str__(self)



# Model - InstituteProgramEntrance
# This model stores for each institute and for each discipline, program and 
# level the Entrance exams used by the Institutes
class InstituteEntranceExam(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    EntranceExam = models.ForeignKey(EntranceExam, on_delete=models.SET_NULL, 
        blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, default='')
     
    def __str__(self):
        return models.Model.__str__(self)


# Model - InstituteImpDates
# When there is no entrance exam record in the EntranceExamImpDates,  This model stores 
# for the institute the important dates
class InstituteImpDates(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    event = models.CharField(max_length=500, blank=True, default='')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    remarks= models.CharField(max_length=2000, blank=True, default='')

    def __str__(self):
        return models.Model.__str__(self)    



# Model - Survey
# This model stores for each institute and for each discipline, the survey
# and the rank for the Institute
class Survey(models.Model):
    survey_code = models.CharField(max_length=100, primary_key=True)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    survey_name = models.CharField(max_length=300, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=True, default='')
    
    def __str__(self):
        return models.Model.__str__(self)
    

# Model - SurveyParameters
# This model stores for each survey and year the parameters and their scores
class SurveyParameters(models.Model):
    Survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    year = models.CharField(max_length=4)
    parameter = models.CharField(max_length=300, blank=True, default='')
    score = models.CharField(max_length=30, blank=True, default='')
    Discipline = models.ForeignKey(Discipline, on_delete=models.SET_NULL, null=True)
    Level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return models.Model.__str__(self)


# Model - InstituteRanking
# This model stores for each institute and for each discipline, the survey
# and the rank for the Institute
class InstituteSurveyRanking(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=4, blank=False, null=False)
    Institute = models.ForeignKey(Institute, null=True, on_delete=models.SET_NULL)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    rank = models.CharField(max_length=10, blank=False, null=False)
    
    def __str__(self):
        return models.Model.__str__(self)
    

# Model - InstituteJEERanks
# This model stores for each institute and for each discipline, program, 
# level, and each quota the JEE ranks for the Institute. This applied where the 
# Institutes (primarily IITs, NITs) have JEE ranks cut offs
class InstituteJEERanks(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    year = models.CharField(max_length=4, blank=True, default='')
    quota = models.CharField(max_length=50, blank=True, default='')
    StudentCategory = models.ForeignKey(StudentCategory, on_delete=models.PROTECT, 
        blank=True, null=True)
    opening_rank = models.IntegerField(blank=True, null=True)
    closing_rank = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return models.Model.__str__(self)
    
# Model - JEEMAINdates
# This model stores the important dates for JEE MAIN 
class JEEMAINdates(models.Model):
    year = models.CharField(max_length=4, blank=False)
    event = models.CharField(max_length=500, blank=True, default='')
    event_date = models.DateField(blank=True, null=True)
    event_order = models.IntegerField(blank=True, null=True)
    event_duration_days = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    remarks= models.CharField(max_length=2000, blank=True, default='')
    
    def __str__(self):
        return self.year
    
        
# Model - InstituteCutOffs
# This model stores for each institute and for each discipline, program, 
# level, and each quota the cut off for the Institute. This applied where the 
# Institutes (primarily IITs, NITs) have JEE ranks cut offs
class InstituteCutOffs(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)
    year = models.CharField(max_length=4, blank=False, null=False)    
    quota = models.CharField(max_length=50, blank=True, default='')
    StudentCategory = models.ForeignKey(StudentCategory, on_delete=models.PROTECT, 
        blank=True, null=True)
    cutOff = models.CharField(max_length=500, blank=True, default='')
    
    def __str__(self):
        return models.Model.__str__(self)    


# Model - InstituteAdmRoutes
# This model stores for each institute and for each discipline, program, 
# level, each category and each quota the routes to get the admission to the Institute.
class InstituteAdmRoutes(models.Model):
    id = models.AutoField(primary_key=True)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT)
    adm_route = models.CharField(max_length=500, blank=False, null=False)    
    description = models.CharField(max_length=5000, blank=True, default='')
    
    def __str__(self):
        return models.Model.__str__(self)    


# Model - UserPref
# This model stores the user preferences and all search and other functionality
# for the user will driven off this model    
# It will have an auto generated primary key
class InsttUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)
    Discipline = models.ForeignKey(Discipline, on_delete = models.PROTECT)
    Level = models.ForeignKey(Level, on_delete = models.PROTECT, blank=True, null=True)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT, blank=True, null=True)
    Institute = models.ForeignKey(Institute, on_delete = models.PROTECT)

    def __str__(self):
        return str(self.User)
    
class StudentCategoryUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    StudentCategory = models.ForeignKey(StudentCategory, on_delete=models.CASCADE, 
        blank=True, null=True)

    def __str__(self):
        return models.Model.__str__(self)

class ProgramUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.User)

class LevelUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    Level = models.ForeignKey(Level, on_delete = models.PROTECT)

    def __str__(self):
        return models.Model.__str__(self)

class DisciplineUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    Discipline = models.ForeignKey(Discipline, on_delete = models.PROTECT)

    def __str__(self):
        return models.Model.__str__(self)

class CountryUserPref(models.Model):
    User = models.ForeignKey(User, on_delete = models.CASCADE)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT)

    def __str__(self):
        return models.Model.__str__(self)
 

# Model - ContactForm
# This model stores messages sent by NextSteps users.
# Also, holds our responses/resolutions.
class ContactForm(models.Model):
    name = models.CharField(max_length=150, blank=False, null =False)
    email_id = models.EmailField(blank=False, null=False)
    phone_number = models.CharField(max_length=30, blank=True, default='')
    subject = models.CharField(max_length=200, blank=False, null =False)
    message = models.CharField(max_length=4000, blank=False, null =False)
    msg_datetime = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    response = models.CharField(max_length=4000, blank=True, default='',editable=False)
    resp_datetime = models.DateTimeField(null=True, editable=False)
    reponded_by = models.CharField(max_length=30, blank=True, default='', editable=False)
    
    def __str__(self):
        return self.name


# Model - PromotionCode
# This model stores promotion codes for the promotions that NextSteps runs.
class PromotionCode(models.Model):
    promotion_code = models.CharField(max_length=50, primary_key=True)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)

    class meta:
        unique_together = (('promotion_code', 'start_date'),)
    
    def __str__(self):
        return self.promotion_code

# Model UserAccount
# Stores the registration, subscription, payment related information.
# This model to be used to validate the user's subscription 
class UserAccount (models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE,)
    registration_date = models.DateTimeField(blank=True, null=True)
    subscription_start_date = models.DateTimeField(blank=True, null=True)
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    registration_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    subscription_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    PromotionCode = models.ForeignKey(PromotionCode, on_delete = models.PROTECT, blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    promotion_sys_msg = models.CharField(max_length=2, blank=True, default='')
    payment_txn_status = models.CharField(max_length=10, blank=True, default='')
    payment_txn_id = models.CharField(max_length=250, blank=True, default='')
    payment_txn_amount=models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    payment_txn_posted_hash=models.CharField(max_length=250, blank=True, default='')
    payment_txn_key=models.CharField(max_length=250, blank=True, default='')
    payment_txn_productinfo=models.CharField(max_length=250, blank=True, default='')
    payment_txn_email=models.CharField(max_length=250, blank=True, default='')
    payment_txn_salt=models.CharField(max_length=250, blank=True, default='')
    payment_firstname = models.CharField(max_length=250, blank=True, default='')
    payment_lastname = models.CharField(max_length=250, blank=True, default='')
    payment_email = models.CharField(max_length=250, blank=True, default='')
    payment_phone = models.CharField(max_length=20, blank=True, default='')
    payment_address1 = models.CharField(max_length=250, blank=True, default='')
    payment_address2 = models.CharField(max_length=250, blank=True, default='')
    payment_city = models.CharField(max_length=250, blank=True, default='')
    payment_state = models.CharField(max_length=250, blank=True, default='')
    payment_country = models.CharField(max_length=250, blank=True, default='')
    payment_zip_code = models.CharField(max_length=20, blank=True, default='')


    def __str__(self):
        return str(self.User)

''' Store details before user proceeds to payment.
    To be used to know if user tried to subscribe but didn't go forward with payment '''
class BeforePayment(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE,)
    registration_date = models.DateTimeField(blank=True, null=True)
    registration_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    subscription_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    promotionCode = models.CharField(max_length=50, blank=True, default='')
    discount_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    promotion_sys_msg = models.CharField(max_length=2, blank=True, default='')
    date_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.User)

    
class UserAppDetails(models.Model):    
    
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    )
    
    User = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, blank=False, null=False)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='MALE',
    )
    mothers_name = models.CharField(max_length=200, blank=True, default='')
    mothers_qualification = models.CharField(max_length=200, blank=True, default='')
    mothers_occupation = models.CharField(max_length=200, blank=True, default='')
    mothers_income = models.CharField(max_length=200, blank=True, default='')
    fathers_name = models.CharField(max_length=200, blank=True, default='')
    fathers_qualification = models.CharField(max_length=200, blank=True, default='')
    fathers_occupation = models.CharField(max_length=200, blank=True, default='')
    fathers_income = models.CharField(max_length=200, blank=True, default='')
    StudentCategory = models.ForeignKey(StudentCategory, on_delete=models.PROTECT, 
        blank=True, null=True)
    person_with_disability = models.NullBooleanField(default=False)
    percetage_of_disability = models.DecimalField(max_digits=5, decimal_places=2, 
        blank=True, null=True)
    state_of_eligibility = models.CharField(max_length=200, blank=True, default='')
    nationality = models.CharField(max_length=200, blank=True, default='')
    address = models.CharField(max_length=2000, blank=True, default='')
    locality = models.CharField(max_length=300, blank=True, default='')
    city_town_village = models.CharField(max_length=300, blank=True, default='')
    district = models.CharField(max_length=300, blank=True, default='')
    pin_code = models.PositiveIntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, default = '')
    Country = models.ForeignKey(Country, on_delete = models.PROTECT, 
        blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, default='')
    email_id = models.EmailField(blank=True, default='')
    aadhaar_number = models.CharField(max_length=12, blank=True, default='')
    class_10th_year_of_passing = models.CharField(max_length=4, blank=True, default='')
    class_10th_percentage_cgpa = models.CharField(max_length=25, blank=True, default='')
    class_10th_school_address = models.TextField(max_length=3000, blank=True, default='')
    class_10th_board_or_university = models.CharField(max_length=300, blank=True, default='')
    class_12th_year_of_passing = models.CharField(max_length=4, blank=True, default='')
    class_12th_percentage_cgpa = models.CharField(max_length=25, blank=True, default='')
    class_12th_school_address = models.TextField(max_length=3000, blank=True, default='')
    class_12th_board_or_university = models.CharField(max_length=300, blank=True, default='')
    guardians_name = models.CharField(max_length=300, blank=True, default='')
    guardians_qualification = models.CharField(max_length=200, blank=True, default='')
    guardians_occupation = models.CharField(max_length=200, blank=True, default='')
    guardians_income = models.CharField(max_length=200, blank=True, default='')
    candidate_photo = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    candidate_signature = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    parent_signature = models.ImageField(upload_to='uploads/%Y/%m/%d/',  blank=True, null=True)
    
    def __str__(self):
        return models.Model.__str__(self)
    


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    )
    
    User = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    date_of_birth = models.DateField(null=True, blank=True, default='')
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='MALE',
    )
    address = models.CharField(max_length=2000, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=30, blank=True, default='')
    education = models.CharField(max_length=30, blank=True, default='')

    def __str__(self):
        return str(self.User)
    
    
class UserCalendar(models.Model):
    id = models.DecimalField(primary_key=True, max_digits=30, decimal_places=25)
    User = models.ForeignKey(User, on_delete=models.CASCADE,)
    Institute = models.ForeignKey(Institute, on_delete=models.PROTECT,blank = True,null=True)
    Country = models.ForeignKey(Country, on_delete = models.PROTECT,blank = True,null=True)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT,blank = True,null=True)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT,blank = True,null=True)
    Program = models.ForeignKey(Program, on_delete=models.PROTECT,blank = True,null=True)
    event = models.CharField(max_length=500, blank=True, default='')
    event_date = models.DateField(blank=True, null=True)
    event_order = models.IntegerField(blank=True, null=True)
    event_duration_days = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    remarks= models.CharField(max_length=2000, blank=True, default='')

    class meta:
        unique_together = (('User', 'event', 'event_date'),)
    
    def __str__(self):
        return str(self.User)   

class ReferNextSteps(models.Model):
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE,)
    name = models.CharField(max_length=150, blank=False, null=False)
    email_id = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    message = models.CharField(max_length=2000, blank=False, null=False)

    def __str__(self):
        return str(self.User)   

class Subjects(models.Model):
    Country = models.ForeignKey(Country, on_delete = models.PROTECT,blank = True,null=True)
    Discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT,blank = True,null=True)
    Level = models.ForeignKey(Level, on_delete=models.PROTECT,blank = True,null=True)
    subject = models.CharField(max_length=2000, blank=False, null=False)
    

class UserStudySchedule(models.Model):
    User =  models.ForeignKey(User, on_delete=models.CASCADE)
    study_days_per_week = models.PositiveIntegerField(blank=True, null=True,
            validators=[validate_max7days])
    study_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, 
        blank=True, null=True, validators=[validate_max24hrs])
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class meta:
        unique_together = (('User', 'date_updated'),)
    

class UserSubjectSchedule(models.Model):
    User =  models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=2000, blank=False, null=False)
    percentage_weight = models.DecimalField(max_digits=3, decimal_places=0, 
            blank=True, null=True, validators=[validate_max100],
            verbose_name="Allocation(%)")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    
    class meta:
        unique_together = (('User', 'subject', 'date_updated'),)

class UserDaySchedule(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=2000, blank=False, null=False)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    planned_hours = models.DecimalField(max_digits=4, decimal_places=2, 
            blank=True, null=True, validators=[validate_max24hrs])
    date_updated = models.DateTimeField(blank=True, null=True)
    schedule_generated = models.NullBooleanField(default=False)
    schedule_generated_date = models.DateTimeField(blank=True, null=True)
    mon = models.NullBooleanField(blank=True, null=True)
    tue = models.NullBooleanField(blank=True, null=True)
    wed = models.NullBooleanField(blank=True, null=True)
    thu = models.NullBooleanField(blank=True, null=True)
    fri = models.NullBooleanField(blank=True, null=True)
    sat = models.NullBooleanField(blank=True, null=True)
    sun = models.NullBooleanField(blank=True, null=True)

    class meta:
        unique_together = (('User', 'subject', 'date_updated'),)
    
    
class StudyHours(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=2000, blank=False, null=False)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    planned_hours = models.DecimalField(max_digits=4, decimal_places=2, 
            blank=True, null=True, validators=[validate_max24hrs])
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, 
            blank=True, null=True, validators=[validate_max24hrs])
    date_updated = models.DateTimeField(blank=True, null=True) 

    class meta:
        unique_together = (('User', 'subject', 'date', 'date_updated'),)
