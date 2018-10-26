from django.conf.urls import url, include

from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from allauth.account.views import LoginView

#from NextSteps.payment_views import paymentForm, success, failure

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.NextStepslogin, name='login'),
    #url(r'^home/$', views.loggedIn_index, name='loggedInHome'),
    
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),    
    
    url(r'^accounts/', include('allauth.urls')),
    
    url(r'^password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),    
    url(r'^password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    
    url(r'^reset/$', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'), name='password_reset'),
    url(r'^reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
       auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
       name='password_reset_confirm'),
    url(r'^reset/complete/$',
       auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
       name='password_reset_complete'), 

    url(r'^contactus/$', views.contactUs, name='contact_us'),
    url(r'^contactusconfirm/$', views.contactUsConfirm, name='contact_us_confirm'),

    url(r'^register/$', views.checkSubscription, name='checkSubscription'),

    
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^MyProfile/$', views.userProfile, name='user_profile'),
    url(r'^ProfileSave/$', views.userProfileConfirm, name='userProfile_Confirm'),


    url(r'^userprefs/$', views.userPref, name='prefs'),
    url(r'^userprefconfirm/$', views.userPrefConfirm, name='prefConfirm'),
    url(r'^ajax/GetInstts/$', views.getInstitutes, name='Get_Instts'),    
    url(r'^ajax/GetPrograms/$', views.getPrograms, name='Get_Programs'),    
    url(r'^ajax/GetSeatPrograms/$', views.getSeatQuotaPrograms, name='Get_SeatQuota_Programs'),    


    url(r'^institutelist/$', views.InsttList, name = 'instt_list'),
    #url(r'^insttdetails/(?P<instt_code>\d+)/$', views.instt_all_details, name = 'instt_all_details'),
    url(r'^insttdetails/$', views.instt_all_details, name = 'instt_all_details'),
    url(r'^compareInstitutess/$', views.compare_instts, name = 'compare_instts'),
    url(r'^ajax/add_to_preferences/$', views.add_to_preferences, name='add_to_preferences'),    

    url(r'^ajax/Get_Instt_States_Cities/$', views.insttStatesCities, name='get_instt_states_cities'),    

    url(r'^ajax/InstituteListUnregistered/$', views.InstitueListUnRegistered, name='InstitueListUnRegistered'),    


    url(r'^featureSearchInstt/$', views.feature_instt_search, name = 'feature_instt_search'),
    url(r'^featureImportantInfo/$', views.feature_important_info, name = 'feature_important_info'),
    url(r'^featureCalendar/$', views.feature_calendar, name = 'feature_calendar'),
    url(r'^featureSeatChances/$', views.feature_seat_chances, name = 'feature_seat_chances'),
    url(r'^featureSearchInstt/$', views.feature_important_info, name = 'feature_user_app_details'),
    url(r'^featureStudyPlanner/$', views.feature_study_planner, name = 'feature_study_planner'),
    url(r'^featureSearchInstt/$', views.feature_important_info, name = 'feature_compare_instts'),
    url(r'^featureApplicationRecord/$', views.feature_application_record, name = 'feature_application_record'),


    #url(r'^JEERanksFilter/$', views.JEERanksFilter, name='JEE_ranks_filter'),
    #url(r'^JEERanks/$', views.JEEOpeningClosingRanks, name='JEE_ranks'),
    url(r'^JEE_Ranks/$', views.JEERanks, name='JEE_ranks'),
    
    url(r'^InstituteRankings/$', views.insttRankingFilter, name='instt_ranking_filter'),
    url(r'^ProgramResults/$', views.searchProgram, name='program_search_results'),
    url(r'^EntranceExams/$', views.searchEntranceExams, name='search_entrance_exams'),
    url(r'^instts_by_entrance_exam_code/$', views.instts_by_entrance_exam_code, name='instts_by_entrance_exam_code'),



    url(r'^ajax/GetJeeRankYears/$', views.getJeeRankYears, name='jee_rank_years'),    
    
    url(r'^ajax/GetCities/$', views.getCitiesforStates, name='Get_Cities'),    
    
    url(r'^preferredInsttDetails/$', views.preferredInsttDetails, name='preferred_Instt_Details'),
    url(r'^preferredInsttEntrance/$', views.preferredInsttEntrance, name='preferred_Instt_Entrance'),
    url(r'^preferredInsttImpDates/$', views.preferredInsttImpDates, name='preferred_Instt_ImpDates'),
    url(r'^preferredInsttAdmRoutes/$', views.preferredInsttAdmRoutes, name='preferred_Instt_adm_routes'),
    url(r'^preferredInsttConsReport/$', views.preferredInsttConsRep, name='preferred_Instt_cons_report'),
    url(r'^ifThenAnalysis/$', views.ifThenAnalysis, name='if_then_analysis'),
    url(r'^ifThenAnalysisResults/$', views.ifThenAnalysisResults, name='if_then_analysis_results'),
    url(r'^ajax/getInsttProgramByType/$', views.getInsttProgramByType, name='get_instt_progs_by_type'),
    url(r'^ajax/getUserInsttProgramByType/$', views.getUserInsttProgramByType, name='get_user_instt_progs_by_type'),
    url(r'^studyPlanner/(?P<active_tab>\w*)/$', views.studyPlanner, name='study_planner'),
    url(r'^getUserSubjectSchedule/$', views.getUserSubjectSchedule, name='getUserSubjectSchedule'),
    url(r'^getStudyHours/$', views.getStudyHours, name='getStudyHours'),
    url(r'^saveStudyHours/$', views.saveStudyHours, name='save_studyhours'),
    url(r'^saveLoggedHours/$', views.saveLoggedHours, name='save_LoggedHours'),
    url(r'^printStudySchdule/$', views.printStudySchedule, name='print_study_schedule'),
    url(r'^updateStudySchedule/$', views.updateStudySchedule, name='update_study_schedule'),
    url(r'^ajax/getMonthStudyHours/$', views.getMonthStudyHours, name='getMonthStudyHours'),
    url(r'^ajax/getMonthSubjHours/$', views.getMonthSubjHours, name='getMonthSubjHours'),
    url(r'^ajax/getDayRows/$', views.getDayRows, name='getDayRows'),
    url(r'^ajax/saveStudySchedule/$', views.saveStudySchedule, name='saveStudySchedule'),
    url(r'^ajax/saveSubjSch/$', views.saveSubjSch, name='saveSubjSch'),
    url(r'^ajax/saveDaySch/$', views.saveDaySch, name='saveDaySch'),
    url(r'^ajax/generate_sch_calendar/$', views.generateSchCalendar, name='generate_sch_calendar'),


    url(r'^ajax/getInsttsForPrograms/$', views.getInsttsForProgs, name='get_insttsForProgs'),
    url(r'^ajax/getProgsForInstts/$', views.getProgsForInstts, name='get_progsForInstts'),



    url(r'^findRanks/$', views.JEE_prog_instt_rank_filter, name='JEE_prog_instt_rank_filter'),
    url(r'^rankRsults/$', views.JEE_prog_instt_rank_results, name='JEE_prog_instt_rank_results'),

    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^todolist/$', views.toDoList, name='to_do_list'),
    url(r'^ajax/getUserInstts/$', views.getUserInstts, name='get_user_instts'),
    url(r'^ajax/saveEvents/$', views.save_user_events, name='save_user_events'),
    url(r'^ajax/getInsttsDates/$', views.getInsttImpDates, name='getInsttImpDates'),
    url(r'^ajax/deleteCalendarEvents/$', views.delCalendarEventsByIDs, name='delCalendarEventsByIDs'),
    
    
    url(r'^userAppDetails/$', views.userAppDetailsView, name='user_app_details'),
    url(r'^userAppDetailsConfirm/$', views.userAppDetailsConfirm, name='user_app_confirm'),
    
    url(r'^user_guide/$', views.user_guide, name='user_guide'),

    url(r'^refer/$', views.referNextSteps, name='refer_NextSteps'),
    url(r'^referdone/$', views.referNextSteps_confirm, name='referNextSteps_confirm'),


    url(r'^subscription/$', views.subscription, name='subscription'),
    url(r'^ajax/GetPromo/$', views.getPromoDetails, name='Get_Promo_Details'),    
    
    url(r'^subscription_begin/$', views.subscriptionBegin, name='subscription_begin'),
    url(r'^payment_details/$', views.payment_details, name='payment_details'),
    url(r'^payment_submit/$', views.payment_submit, name='payment_submit'),
    url(r'^payment_submit_nocost/$', views.payment_submit_nocost, name='payment_submit_nocost'),
    url(r'^payment_unsuccessful/$', views.payment_unsuccessful, name='payment_unsuccessful'),
                                       
    url(r'^userAccount/$', views.userAccountInformation, name='user_account'),
    url(r'^renewSubscription/$', views.renewSubscription, name='renew_subscription'),
    url(r'^SubscriptionConfirm/$', views.renewSubscriptionConfirm, name='renew_subscription_confirm'),


    #url(r'^payment_details/', paymentForm),
    #url(r'^Success/', success),
    #url(r'^Failure/', failure),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    