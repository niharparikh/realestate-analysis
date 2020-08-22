import requests
import json
import xmltodict

setVars = {
    'zws-id': '{ID}',
    'address': '561 Joseph East Lowery Boulevard NW',
    'citystatezip': 'Atlanta, GA 30314',
    'rentzestimate': 'true'
}

url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'

r = requests.get(url, params=setVars)
o = xmltodict.parse(r.text)

data = json.dumps(o, sort_keys=True, indent=4)
# zpid = o['zpid']
print(data)