import requests, json, time, datetime, random
from bs4 import BeautifulSoup as bs


def now():
	return (str(datetime.datetime.now()))

cartHeader={
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-origin",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
	"x-requested-with": "XMLHttpRequest"
}

addressHeader={
	"origin": "https://www.snipes.com",
	"referer": "https://www.snipes.com/checkout?stage=shipping",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-origin",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
	"x-requested-with": "XMLHttpRequest"
}

submitOrder={
	"origin": "https://www.snipes.com",
	"pragma": "no-cache",
	"referer": "https://www.snipes.com/checkout?stage=placeOrder",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-origin",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
	"x-requested-with": "XMLHttpRequest",
}

paymHeader={
	"origin": "https://www.snipes.com",
	"pragma": "no-cache",
	"referer": "https://www.snipes.com/checkout?stage=payment",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-origin",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
	"x-requested-with": "XMLHttpRequest"
}

indexProxy = 0 
def getProxy(task_id):
	global indexProxy
#
	try:
		x=open("proxies.txt", 'r')
		lines=x.readlines()
		proxy=random.choice(lines)
		return proxy


		lines=x.readlines()
	except:
		print(str(datetime.datetime.now())+" [TASK {}] < [INFO] No proxies loaded, running with localhost.".format(task_id))



def proxies(s, task_id):
	getProxy(task_id)

	try:
		prox = getProxy(task_id)
		prox = prox.replace("\n","")
		proxies = {
			'http': 'http://'+str(prox),
			'https': 'http://'+str(prox),
		}
		proxies=proxies

		s.proxies = proxies
		print(str(datetime.datetime.now())+" [TASK {}] < [INFO] Parsing proxies.".format(task_id))
	except:
		pass

class Sniper():
	def __init__(this,url,pid,variationId,size,profile):
		this.link=url
		this.sizeId=variationId
		this.pid=pid
		this.size=size
		this.ua={"user-agent":cartHeader['user-agent']}
		this.atcHeader=cartHeader
		this.addressHeader=addressHeader
		this.retrydelay=1
		this.profile=profile
		this.paymHeader=paymHeader
		this.submOrder=submitOrder

	def task(this,task_id):

		s=requests.session()
		proxies(s,task_id)

		def atcCall(this,):
			try:
				print(now()+" [TASK {}] < [INFO] Attempting ATC.".format(task_id))
				this.Data={
					"pid":this.pid, 
					"options": json.dumps([{"optionId":"color","selectedValueId":"black/white/power red"},{"optionId":this.sizeId,"selectedValueId":this.size}]),
					"quantity": "1",
				}
				rr=s.post("https://www.snipes.com/on/demandware.store/Sites-snse-DE-AT-Site/de_DE/Cart-AddProduct?format=ajax", headers=this.atcHeader, data=this.Data,proxies=s.proxies)
				if rr.status_code==200:
					if rr.json()['message']=="Hinzugefügt":
						print(now()+" [TASK {}] < [INFO] Added to cart.".format(task_id))
					else:
						print(now()+" [TASK {}] < [INFO] ATC failed, retrying...".format(task_id))
						time.sleep(this.retrydelay)
						atcCall(this,)
				elif rr.status_code==500:
					print(now()+" [TASK {}] < [INFO] ATC failed, retrying after delay...".format(task_id))
					time.sleep(this.retrydelay)
				elif rr.status_code in [502,503,504]:
					print(now()+" [TASK {}] < [INFO] Request crashed, retrying in %s " % str(this.retrydelay))
					time.sleep(this.retrydelay)
					atcCall(this)
				else:
					print(now()+" [TASK {}] < [INFO] ATC Failed, unknown reason {}".format(task_id,rr.status_code))
			except Exception as e:
				print()
		atcCall(this)


		def paymMethReq(this,csrf):
			try:
				this.data={
					"dwfrm_billing_paymentMethod": "BANK_TRANSFER",
					"dwfrm_giftCard_cardNumber":"", 
					"dwfrm_giftCard_pin":"", 
					"csrf_token":csrf,
					"csrf_token":csrf	
				}
				paymMethReq=s.request('POST',url="https://www.snipes.com/on/demandware.store/Sites-snse-DE-AT-Site/de_DE/CheckoutServices-SubmitPayment?format=ajax",headers=this.paymHeader,data=this.data,proxies=s.proxies)
				if paymMethReq.status_code==200:
					try:
						if paymMethReq.json()['error']==False:
							print(now()+" [TASK {}] < [INFO] Submitted payment method.".format(task_id))
						else:
							print(now()+" [TASK {}] < [INFO] Unable to save payment method.".format(task_id))
							time.sleep(this.retrydelay)
							paymMethReq(this,csrf)


					except KeyError as e:
						print(now()+" [TASK {}] < [INFO] Failed psoting payment method.".format(task_id))
						time.sleep(this.retrydelay)
						paymMethReq(this,csrf)
					except Exception as e:
						print(now()+" [TASK {}] < [INFO] Exception {} occurred posting payment method.".format(task_id,e))
						time.sleep(this.retrydelay)
						paymMethReq(this)
				elif paymMethReq.status_code==403 or paymMethReq.status_code==429:
					print(now()+" [TASK {}] < [INFO] IP banned, switchin proxy.".format(task_id))
					time.sleep(this.retrydelay)
					paymMethReq(this,csrf)
				else:
					print(now()+" [TASK {}] < [INFO] Site error posting payment method,retrying.".format(task_id))
					time.sleep(this.retrydelay)
					paymMethReq(this,csrf)
			except Exception as e:
				print(now()+" [TASK {}] < [INFO] Exception {} occurred posting payment info.".format(task_id,e))
				time.sleep(this.retrydelay)
				paymMethReq(this,csrf)

		def submitAddress(this):
			try:

				reqRsp=s.get("https://www.snipes.com/checkout?stage=shipping#shipping", headers=this.ua,proxies=s.proxies).text
				soup=bs(reqRsp, 'html.parser')
				csrf=soup.find('div',{'data-csrf-name':'csrf_token'})['data-csrf-token']
				this.addyDatz={
					"originalShipmentUUID": "",
					"shipmentUUID": "",
					"dwfrm_shipping_shippingAddress_shippingMethodID": "home-delivery",
					"address-selector": "new",
					"dwfrm_shipping_shippingAddress_addressFields_title": "Herr",
					"dwfrm_shipping_shippingAddress_addressFields_firstName": this.profile['name'],
					"dwfrm_shipping_shippingAddress_addressFields_lastName": this.profile['surname'],
					"dwfrm_shipping_shippingAddress_addressFields_street": f"{this.profile['street']} {this.profile['housenumber']}",
					"dwfrm_shipping_shippingAddress_addressFields_suite": this.profile['housenumber'],
					"dwfrm_shipping_shippingAddress_addressFields_address1": f"{this.profile['street']} {this.profile['housenumber']}",
					"dwfrm_shipping_shippingAddress_addressFields_address2": this.profile['housenumber'],
					"dwfrm_shipping_shippingAddress_addressFields_postalCode": this.profile['cap'],
					"dwfrm_shipping_shippingAddress_addressFields_city": this.profile['city'],
					"dwfrm_shipping_shippingAddress_addressFields_phone": this.profile['phone'],
					"dwfrm_shipping_shippingAddress_addressFields_countryCode": "DE",
					"dwfrm_shipping_shippingAddress_shippingAddressUseAsBillingAddress": "true",
					"dwfrm_billing_billingAddress_addressFields_title": "Herr",
					"dwfrm_billing_billingAddress_addressFields_firstName": this.profile['name'],
					"dwfrm_billing_billingAddress_addressFields_lastName": this.profile['surname'],
					"dwfrm_billing_billingAddress_addressFields_street": f" {this.profile['street']} {this.profile['housenumber']}",
					"dwfrm_billing_billingAddress_addressFields_suite": this.profile['housenumber'],
					"dwfrm_billing_billingAddress_addressFields_address1": f" {this.profile['street']} {this.profile['housenumber']}",
					"dwfrm_billing_billingAddress_addressFields_address2": this.profile['housenumber'],
					"dwfrm_billing_billingAddress_addressFields_postalCode": this.profile['cap'],
					"dwfrm_billing_billingAddress_addressFields_city": this.profile['city'],
					"dwfrm_billing_billingAddress_addressFields_countryCode": "DE",
					"dwfrm_billing_billingAddress_addressFields_phone": this.profile['phone'],
					"dwfrm_contact_email": this.profile['email'],
					"dwfrm_contact_phone": this.profile['phone'],
					"csrf_token":csrf
					}
				req=s.request('POST',"https://www.snipes.com/on/demandware.store/Sites-snse-DE-AT-Site/de_DE/CheckoutShippingServices-SubmitShipping?format=ajax", headers=this.addressHeader, data=this.addyDatz,proxies=s.proxies)
				if req.status_code==200:
					try:
						if req.json()['error']==True:
							print(now()+" [TASK {}] < [INFO] Unable to post address, retrying.".format(task_id))
							time.sleep(this.retrydelay)
							submitAddress(this)
						else:
							print(now()+" [TASK {}] < [INFO] Submitted Address data.".format(task_id))
							paymMethReq(this,csrf)
					except KeyError:
						print(now()+" [TASK {}] < [INFO] Submitted Address data.".format(task_id))
						paymMethReq(this,csrf)
				elif req.status_code==500:
					print(now()+" [TASK {}] < [INFO] Error submitting address, probably missing values.".format(task_id))
				elif req.status_code in [403,429]:
					print(now()+" [TASK {}] < [INFO] IP banned, switchin proxy.".format(task_id))
					time.sleep(this.retrydelay)
					proxies(s,task_id)
					submitAddress(this)
				else:
					print(now()+" [INFO {}] < [INFO] Failed to submit address, site error. ".format(task_id))
					time.sleep(this.retrydelay)
					submitAddress(this)
			except Exception as e:
				print(now()+" [TASK {}] < [INFO] Exception {} occurred submitting address data.".format(task_id,e))
				time.sleep(this.retrydelay)
				submitAddress(this)
			except KeyError:
				print(now()+" [TASK {}] < [INFO] Submitted Address data.".format(task_id))
				submitAddress(this)
		submitAddress(this)


		def submitOrder(this):
			try:
				this.params={
					"format":"ajax"
				}
				this.data={
					"dwfrm_contact_acceptGDPR": "true"
				}

				r=s.request('POST','https://www.snipes.com/on/demandware.store/Sites-snse-DE-AT-Site/de_DE/CheckoutServices-PlaceOrder?format=ajax',headers=this.submOrder,proxies=s.proxies)
				if r.status_code==200:
					if r.json()['error']==False:
						print(now()+" [TASK {}] < [INFO] Order placed successfully, orderNumber = {}".format(task_id,r.json()['orderID']))
					else:
						print(now()+" [TASK {}] < [INFO] Order failed, retrying...".format(task_id))
						time.sleep(this.retrydelay)
						submitOrder(this)
				elif r.status_code in [500,502,503,504]:
					print(now()+" [TASK {}] < [INFO] Request crashed, retrying atfer delay.".format(task_id))
					time.sleep(this.retrydelay)
					submitOrder(this)
				elif r.status_code in [403,429]:
					print(now()+" [TASK {}] < [INFO] Yikes, IP banned, switchin proxies.".format(task_id))
					proxies(s,task_id)
					time.sleep(this.retrydelay)
					submitOrder(this)
				else:
					print(now()+" [TASK {}] < [INFO] Unhandled error, retrying.".format(task_id))
					time.sleep(this.retrydelay)
					submitOrder(this)


			except KeyError:
				print(now()+" [TASK {}] < [INFO] Order error, retrying...".format(task_id))
				time.sleep(this.retrydelay)
				submitOrder(this)
			except Exception as e:
				#copypaste the above shit
				print(now()+" [TASK {}] < [INFO] Order error, retrying...".format(task_id))
				time.sleep(this.retrydelay)
				submitOrder(this)
		submitOrder(this)
