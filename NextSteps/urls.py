from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.NextStepslogin, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
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

    
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^payment/$', views.payment, name='payment'),
    url(r'^ajax/GetPromo/$', views.getPromoDetails, name='Get_Promo_Details'),    
    url(r'^subscriptionstart/$', views.subscriptionStart, name='subscription_start'),
    url(r'^userAccount/$', views.userAccountInformation, name='user_account'),
    url(r'^renewSubscription/$', views.renewSubscription, name='renew_subscription'),
    url(r'^SubscriptionConfirm/$', views.renewSubscriptionConfirm, name='renew_subscription_confirm'),


    url(r'^userprefs/$', views.userPref, name='prefs'),
    url(r'^userprefconfirm/$', views.userPrefConfirm, name='prefConfirm'),
    url(r'^ajax/GetInstts/$', views.getInstitutes, name='Get_Instts'),    
    url(r'^ajax/GetPrograms/$', views.getPrograms, name='Get_Programs'),    
    url(r'^ajax/GetSeatPrograms/$', views.getSeatQuotaPrograms, name='Get_SeatQuota_Programs'),    

    url(r'^SearchFilter/$', views.SearchFilter, name = 'search_filter'),
    url(r'^SearchInstts/', views.SearchInstts, name = 'Search_Instts'),
    url(r'^SearchInsttTypeFilter/$', views.instituteTypeSearchFilter, name = 'instt_type_filter'),
    url(r'^SearchInsttSearch/$', views.instituteTypeSearchResults, name = 'instt_type_search_results'),

    url(r'^InsttsPrograms/$', views.ProgramSeatQuotaDetails, name='Institute_Programs'),


    url(r'^JEERanksFilter/$', views.JEERanksFilter, name='JEE_ranks_filter'),
    url(r'^JEERanks/$', views.JEEOpeningClosingRanks, name='JEE_ranks'),
    url(r'^insttCutOffsFilter/$', views.insttCutOffFilter, name='instt_cut_off_filter'),
    url(r'^insttCutOff/$', views.insttCutOff, name='instt_cut_off'),
    url(r'^InsttRankingFilter/$', views.insttRankingFilter, name='instt_ranking_filter'),
    url(r'^ProgramFilter/$', views.programFilter, name='program_filter'),
    url(r'^ProgramResults/$', views.searchProgram, name='program_search_results'),
    url(r'^SeatQuotaFilter/$', views.seatQuotaFilter, name='seat_quota_filter'),
    url(r'^SeatQuotaResults/$', views.searchSeatQuota, name='seat_quota_search_results'),


    
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

    url(r'^findRanks/$', views.JEE_prog_instt_rank_filter, name='JEE_prog_instt_rank_filter'),
    url(r'^rankRsults/$', views.JEE_prog_instt_rank_results, name='JEE_prog_instt_rank_results'),


    url(r'^userAppDetails/$', views.userAppDetailsView, name='user_app_details'),
    url(r'^userAppDetailsConfirm/$', views.userAppDetailsConfirm, name='user_app_confirm'),

    
]

