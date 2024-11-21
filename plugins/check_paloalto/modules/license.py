## Check license status

from .utils import nagios_msg, XMLreader
from datetime import datetime, timedelta

def create_check(args):
    cmd = '<request><license><info></info></license></request>'
    xmldata = XMLreader(args.host, args.token, cmd)
    data = xmldata.read()
    days = args.days
    get_license_status(data,days)

def safe_get_text(element, tag_name):
    """Safely get text from an element, returning an empty string if not found."""
    tag = element.find(tag_name)
    return tag.text if tag else ''


def get_license_status(data,days):
    
    today = datetime.now()
    licenses = data.find_all('entry')
    license = []
    license_expired = []
    license_expiring = []
    days = int(days) if days != None else 30

    for license_entry in licenses:
        feature = safe_get_text(license_entry, 'feature')
        description = safe_get_text(license_entry, 'description')
        issued = safe_get_text(license_entry, 'issued')
        expires = safe_get_text(license_entry, 'expires')
        expired = safe_get_text(license_entry, 'expired')

        # Convert expires date to datetime object
        try:
            expires_date = datetime.strptime(expires, '%B %d, %Y')
        except:
            expires_date = 'Never'

        # Check if expires date is within 30 days
        if expired == 'yes': 
            license_expired.append(f'The license for {feature} has expired {expires} ') 

        elif expires_date != 'Never' and expires_date <= today + timedelta(days=days):
            license_expiring.append(f'The license for {feature} is expiring {expires}')
    
        licence_data= f'{feature}: {description}, Issued: {issued}, Expires: {expires}, Expired: {expired}'
        license.append(licence_data)

    if license_expired:
        nagios_msg(2,f'Critical - Licenses expired: {license_expired}')
        print(f)
    if license_expiring: 
        nagios_msg(1,f'Warning - Licenses expiring: {license_expiring}')
    else:
        nagios_msg(0,f'OK - Happy days: {license}')

