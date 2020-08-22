import requests
import json
import numpy

neighborhoods = ['Midtown', 'Atlantic Station', 'Downtown', 'Little Five Points', 'Virginia-Highland', 'Buckhead', 'Inman Park', 'Peachtree Park', 'Lindbergh', 'Old Fourth Ward', 'Piedmont Heights', 'Cabbagetown']

for neighborhood in neighborhoods:
    setVars = {
        'client_id': '{KEY}',
        'locale': 'en-US',
        'currency': 'USD',
        '_format': 'for_search_results',
        '_limit': 50,
        '_offset': 0,
        'guests': '2',
        'ib': 'false', # instant book
        'ib_add_photo_flow': 'true',  # unsure what this is
        'location': neighborhood + ', Atlanta, GA',
        'min_bathrooms': 1,
        'min_bedrooms': 0,
        'min_beds': 1,
        'price_min': 10,
        'price_max': 1000,
        'min_num_pic_urls': 2,
        'sort': 1, # 1 for forward, 0 for reverse
        'suppress_facets': 'true',  # unsure what this is
        # 'user_lat':	33.782092,  # Latitude search coordinate 33.782092, -84.385783
        # 'user_lng':	-84.385783  # Longitude search coordinate
    }

    url = 'https://api.airbnb.com/v2/search_results'
# print(url + urllib.urlencode(setVars))

    r = requests.get(url, params=setVars)
    data = r.json()

    prices = []

    for x in range(len(data['search_results'])):
        if data['search_results'][x]['listing']['room_type'] == 'Entire home/apt':
            if data['search_results'][x]['listing']['person_capacity'] <= 4:
                prices.append(data['search_results'][x]['pricing_quote']['localized_nightly_price'])

    median_rate = numpy.median(prices)
    revenue = median_rate * 30 * 0.7 * 0.97
    costs = 175 + 250
    cash_flow = revenue - costs
    print('Median rate: ' + repr(median_rate) + '\nMonthly cash flow in ' + neighborhood + ' is: ' + repr(cash_flow) + '\n--------------\n\n')

# print(json.dumps(data, sort_keys=True, indent=4))


