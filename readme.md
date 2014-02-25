# Apilog

## Description
Simple django application to store log data through a REST API in mongoDB. Developed in django, django-rest-framework, running through gunicorn and storing data in mongodb. Also using nginx to have proxypass from http to https.

## Architecture
[Architecture](https://github.com/jalp/apilogger/wiki)

## Requeriments

libevent lib is needed, so it has to be installed in your machine:

* On Mac: brew install libevent
* On Linux: sudo apt-get install libevent-dev

Needed packages:

- Django==1.6.1
- argparse==1.1
- coverage==3.7.1
- dateutils==0.6.6
- django-nose==1.2
- django-log-request-id==1.0.0
- djangorestframework==2.3.12
- gevent==1.0
- greenlet==0.4.2
- gunicorn==18.0
- mock==1.0.1
- nose==1.3.0
- pymongo==2.6.3
- python-dateutil==2.2
- pytz==2013.9
- six==1.5.2
- wsgiref==0.1.2

## gUnicorn configuration
	import multiprocessing

	bind = '0.0.0.0:8000'
	workers = multiprocessing.cpu_count() * 2 + 1
	worker_class = 'gevent'
	loglevel = 'debug'
	backlog = 2048
	errorlog = '/opt/bvp/log/gunicorn-error.log'
	accesslog = '/opt/bvp/log/gunicorn-access.log'
## Nginx configuration
I use Nginx as proxy_pass to redirect all the service requests from http to https.  
[Here](https://gist.github.com/jalp/9093810) you can find it (I upload a gist with the code) 
## Simple stress test
#### Plain text
Insert 50000 text plain data log into database

>time for i in $(seq 1 50000); do curl -k -i -L -X POST -H 'Content-Type: text/plain' -d '2013/10/11T11:48:50.860 2013/10/11T11:48:50.898 M2M 5f4e6060-58d5-443c-bafd-3f09ba532f28 BE MobileId / 21407 INFOSTATS 400 [{"MobileId":{"info":{"userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36","xff":"10.70.15.127, 46.233.72.114","contentType":null}}}] ' http://localhost:8000/partnerprovisioning/v1/log/; done

##### Result:

real	11m53.015s

user	4m17.710s

sys		3m20.521s

#### JSON
Insert 50000 json data log into database

>time for i in $(seq 1 50000); do curl -k -i -L -X POST -H "Content-Type: application/json" -d '{"origin": "BE", "body": [{"MobileId": {"info": {"userAgent": "Apache-HttpClient/4.1.1 (java 1.5)", "contentType": "application/json", "xff": null}}}], "http_request": {}, "responseDate": "2013-07-30T14:10:09.154Z", "api": "mobileid", "app": "MobileId", "domain": null, "serviceId": "", "requestDate": "2013-07-30T14:10:08.617Z", "body_request":{"msisdn": ""}, "responseCode": "400", "appId": "", "transactionId": "2bf76d13-883a-419e-bfb3-f9a05e83928e", "id": 81,"statType": "INFOSTATS"}' http://localhost:8000/partnerprovisioning/v1/log/; done

##### Result
real	10m32.990s

user	4m12.961s

sys		3m18.107s