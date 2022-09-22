import base64
from datetime import datetime
import math
from pysendpulse.pysendpulse import PySendPulse

def mailing():
    REST_API_ID = 'e071900fe5ab9aa6dd4dec2f42160ead'
    REST_API_SECRET = '7e82daa1ccfd678487a894b3e3487967'
    TOKEN_STORAGE = 'memcached'
    MEMCACHED_HOST = '127.0.0.1:11211'
    SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
    return SPApiProxy

def get_adressbooks():
    SPApiProxy = mailing()
    return SPApiProxy.get_list_of_addressbooks(offset=0, limit=20)

def get_emails():
    SPApiProxy = mailing()
    return [d['email'] for d in SPApiProxy.get_list_of_senders()]

def send_campaign(from_email, from_name, subject, body, emails, attachments=None):
    SPApiProxy = mailing()
    addressbooks = SPApiProxy.get_list_of_addressbooks(limit=100)
    
    #Находим книгу
    status = ''
    for i in range(10):
        for addressbook in addressbooks:
            if addressbook['name'] == f'Координатор (автоматический-{i+1})':
                addressbook = SPApiProxy.get_addressbook_info(addressbook['id'])[0]
                break
        if addressbook['status'] == 0:
            status = 'ok'
            break
    
    if status == 'ok':
        #Удаляем контакты из книги
        for i in range(math.ceil(addressbook['all_email_qty']/100)):
            old_emails = SPApiProxy.get_emails_from_addressbook(addressbook['id'], limit=100, offset=i*100)
            old_emails = [d['email'] for d in old_emails]
            SPApiProxy.delete_emails_from_addressbook(addressbook['id'], old_emails)
        #Добавляем новые контакты в книгу
        SPApiProxy.add_emails_to_addressbook(addressbook['id'], emails)

        body = bytes(body, 'utf-8')
        campaign = SPApiProxy.add_campaign(
            from_email=from_email,
            from_name=from_name,
            subject=subject,
            body=body,
            addressbook_id=addressbook['id'],
            campaign_name=f'Координатор ({datetime.today()})'
        )
        SPApiProxy.get_list_of_addressbooks()
        if 'status' in campaign:
            return campaign['status']
        else:
            return f'{campaign["data"]["error_code"]}: {campaign["data"]["message"]}'
    return "BisyError"