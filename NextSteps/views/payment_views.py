from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, Template,RequestContext
import datetime
import hashlib
from random import randint
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
#from django.core.context_processors import csrf
from django.template.context_processors import csrf
from django.contrib.auth.models import User

from NextSteps.models import UserAccount, PromotionCode, BeforePayment 
from NextSteps.decorators import subscription_active, subscription_not_active

from .common_views import *


MERCHANT_KEY = "oeIVpyez"
key=""
SALT = "kJZV7rwzYo"
PAYU_BASE_URL = "https://sandboxsecure.payu.in/_payment"


@login_required
@subscription_not_active
def payment_details(request):


	# Get logged in user id
	user = getLoggedInUserObject(request)

	reg_found = False
	phone_number = ''
	
	useraccount = UserAccount.objects.filter(User=user).order_by('-subscription_end_date')

	# Get latest subscription end date
	acct = useraccount.order_by('-subscription_end_date')[:1]
	
	'''
	Check if the subscription is already active, if so, render the subscription active page
	else proceed to paymentForm submission page
	'''
	if isSubsActive(request):
		username = request.user
		
		subs_end_dt = datetime.datetime.strptime("1900-11-01T01:01:01-0100", "%Y-%m-%dT%H:%M:%S%z")
	
		for ua in acct:
			phone_number = ua.phone_number
			subs_end_dt = ua.subscription_end_date
			reg_found = True
	
		subs_end_dt1 = subs_end_dt.strftime("%d-%m-%Y")
		
		if subs_end_dt < timezone.now():
			subs_active = False
		else:
			subs_active = True
	
		return render(request, 'NextSteps/subcription_already_active.html', {'useraccount':useraccount, 
				'reg_found':reg_found, 'subs_end_dt':subs_end_dt, 
				'subs_active': subs_active})


	'''''''''''''''''''''''''''''''''''''''''''''''
	Create Payment Form and render
	'''''''''''''''''''''''''''''''''''''''''''''''
	
	action = ''
	posted={}
	# Merchant Key and Salt provided y the PayU.

	for i in request.POST:
		posted[i]=request.POST[i]
	
	user = get_object_or_404(User, username=request.user)			
	posted['firstname'] = user.first_name
	posted['lastname'] = user.last_name
	posted['amount'] = request.POST.get('totalFee', '0')
	posted['email'] = user.email
	posted['phone'] = phone_number
	posted['productinfo'] = 'NextSteps Subscription'
	posted['surl'] = 'http://localhost:7000/subscription_begin/'
	posted['furl'] = 'http://localhost:7000/payment_unsuccessful/'
	posted['service_provider'] = 'NextSteps Solutions'
	posted['curl'] = 'http://localhost:7000/payment_unsuccessful/'
	posted['udf1'] = request.POST.get("promoCode",'').upper()
	udf2 = request.POST.get('percentDisc', '0')
	posted['udf3'] = request.POST.get('promocode_err_msg', '')
	posted['udf4'] = user.last_name

	
	if udf2 == '':
		posted['udf2'] = '0'
	else:
		posted['udf2'] = udf2
		
	''' Let's save this info before proceeding to payment.'''
	prePay = BeforePayment (
					User = user,
					registration_date = datetime.datetime.now(),
					total_amount = posted['amount'], 
					promotionCode = posted['udf1'],
					discount_percent = float(posted['udf2']), 
					promotion_sys_msg = posted['udf3'],
					date_updated = datetime.datetime.now() 
					)
	
	prePay.save()
	
	return render (request, 'NextSteps/payment_details.html', {"posted":posted})

@login_required
@subscription_not_active
def payment_submit(request):
	
	'''''''''''''''''''''''''''''''''''''''''''''''
	Create Payment Form and submit (it is to get auto submitted when rendered)
	'''''''''''''''''''''''''''''''''''''''''''''''
	
	action = ''
	posted={}
	# Merchant Key and Salt provided y the PayU.

	for i in request.POST:
		posted[i]=request.POST[i]

	
	user = get_object_or_404(User, username=request.user)			
	posted['firstname'] = request.POST.get("firstname",'')
	posted['lastname'] = request.POST.get("lastname",'')
	posted['amount'] = request.POST.get('amount', '0')
	posted['email'] = request.POST.get("email",'')
	posted['phone'] = request.POST.get("phone",'')
	posted['productinfo'] = 'NextSteps Subscription'
	posted['surl'] = 'http://localhost:7000/subscription_begin/'
	posted['furl'] = 'http://localhost:7000/payment_unsuccessful/'
	posted['service_provider'] = 'NextSteps Solutions'
	posted['curl'] = 'NextSteps/payment_aborted.html'
	posted['udf1'] = request.POST.get("udf1",'').upper()
	udf2 = request.POST.get('udf2', '')
	posted['udf3'] = request.POST.get('udf3', '')
	posted['udf4'] = request.POST.get('lastname', '')
	posted['udf5'] = request.POST.get('state', '')

	if udf2 == '':
		posted['udf2'] = '0'
	else:
		posted['udf2'] = udf2
		
	
	hash_object = hashlib.sha256(b'randint(0,20)')
	txnid=hash_object.hexdigest()[0:20]
	hashh = ''
	posted['txnid']=txnid
	hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
	posted['key']=key
	hash_string=''
	hash_string+= MERCHANT_KEY
	
	hashVarsSeq=hashSequence.split('|')
	for i in hashVarsSeq:
		try:
			hash_string+=str(posted[i])
		except Exception:
			hash_string+=''
		hash_string+='|'
	hash_string+=SALT
	hashh=hashlib.sha512(hash_string.encode('utf8')).hexdigest().lower()
	action =PAYU_BASE_URL

	if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("productinfo")!=None and posted.get("firstname")!=None and posted.get("email")!=None):
		return render (request, 'NextSteps/payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":PAYU_BASE_URL })
	else:		
		return render (request, 'NextSteps/payment_submit.html', {"posted":posted,"hashh":hashh,
						"MERCHANT_KEY":MERCHANT_KEY,"txnid":txnid,"hash_string":hash_string,
						"action":"." })

@csrf_protect
@csrf_exempt
@subscription_not_active
def subscriptionBegin(request):
	c = {}
	c.update(csrf(request))
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt="GQs7yium"
	
	
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()
	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
	else:
		print ("Thank You. Your order status is ", status )
		print ("Your Transaction ID for this transaction is ",txnid)
		print ("We have received a payment of Rs. ", amount ,". Your order will soon be shipped.")


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''' Let's save the payment details and create the user account '''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	# Get logged in user id
	userid = User.objects.filter(username = request.user).values('id')
	user = get_object_or_404(User, username=request.user)
	
	# Get registration, subscription, payment, promotion code details from the request
	subsFee = float('250')
	totalFee = float(request.POST.get("amount",0))
	regFee = totalFee - subsFee
	promoCode = request.POST.get("udf1",'').upper() # always use promo code in CAPS
	percentDisc= request.POST.get("udf2",'0')
	promocode_err_msg = request.POST.get("udf3",'')
	mode = request.POST.get("mode")
	phone = request.POST.get("phone")
	firstname = request.POST.get("firstname")
	lastname = request.POST.get("udf4")	  #For PayUmoney, lastname is not coming back, so using udf4 for the same
	email = request.POST.get("email")
	address1 = request.POST.get("address1")
	address2 = request.POST.get("address2")
	city = request.POST.get("city")
	state = request.POST.get("udf5") #For PayUmoney, state is not coming back, so using udf4 for the same
	country = request.POST.get("country")
	zipcode = request.POST.get("zipcode")
	
	if percentDisc == '':
		percentDisc = '0'

			
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
	# Calling add_year method twice as the subscription period is 2 years.
	subs_end = add_year(datetime.datetime.now())
	subs_end = add_year(subs_end)


	#Set default as status PASS and the success message
	pass_fail = 'PASS'	  
	msg = ''

	try:
		# Save the registration, subscription, payment, promotion code details 
		useracct = UserAccount(User=user, 
					registration_date = datetime.datetime.now(),
					subscription_start_date = datetime.datetime.now(), 
					subscription_end_date = subs_end, 
					payment_date = datetime.datetime.now(),
					registration_amount = regFee, 
					subscription_amount = subsFee,
					total_amount = totalFee, 
					PromotionCode = promo,
					discount_percent = float(percentDisc), 
					promotion_sys_msg = promocode_err_msg,
					payment_txn_status = status,
					payment_txn_id = txnid,
					payment_txn_amount=totalFee,
					payment_txn_posted_hash=posted_hash,
					payment_txn_key=key,
					payment_txn_productinfo=productinfo,
					payment_txn_email=email,
					payment_txn_salt=salt,
					payment_firstname = firstname,
					payment_lastname = lastname,
					payment_email = email,
					payment_phone = phone,
					payment_address1 = address1,
					payment_address2 = address2,
					payment_city = city,
					payment_state = state,
					payment_country = country,
					payment_zip_code = zipcode
				)

		useracct.save()
		pass_fail = 'PASS'

	except Error as e:
		msg = 'Apologies!! Could not record your subscription. Not to worry though. Our team will have your subscription created. Please feel free to contact us at support@NextSteps.co.in'
		pass_fail = 'FAIL'

		
	return render(request, 'NextSteps/subscription_begin.html',
				{ "txnid":txnid, "status":status, "amount":amount, 'msg':msg,
				'pass_fail':pass_fail, 'firstname':firstname }
		)


@csrf_protect
@csrf_exempt
@login_required
@subscription_not_active
def payment_unsuccessful(request):
	c = {}
	c.update(csrf(request))
	status=request.POST["status"]
	firstname=request.POST["firstname"]
	amount=request.POST["amount"]
	txnid=request.POST["txnid"]
	posted_hash=request.POST["hash"]
	key=request.POST["key"]
	productinfo=request.POST["productinfo"]
	email=request.POST["email"]
	salt=""
	try:
		additionalCharges=request.POST["additionalCharges"]
		retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	except Exception:
		retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
	
	hashh=hashlib.sha512(retHashSeq.encode('utf8')).hexdigest().lower()

	if(hashh !=posted_hash):
		print ("Invalid Transaction. Please try again")
	else:
		print ( "Thank You. Your order status is ", status )
		print ( "Your Transaction ID for this transaction is ",txnid )
		print ( "We have received a payment of Rs. ", amount ,". Your order will soon be shipped." )

	return render(request, "NextSteps/payment_unsuccessful.html", {"status":status, 
					"amount":amount, 'firstname':firstname, 'txnid':txnid})

