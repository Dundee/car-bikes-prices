import datetime
import json
from lxml import html
import logging
import re
import statistics

import requests

BIKES = {
    'Suzuki DL 650 V-Strom': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=suzuki&s%5Bmodel%5D=suzuki-dl-650-v-strom',
    'Suzuki SV 650S': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=suzuki&s%5Bmodel%5D=suzuki-sv-650s',
    'Suzuki SV 650': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=suzuki&s%5Bmodel%5D=suzuki-sv-650',
    'Suzuki GSX-R 1000': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=suzuki&s%5Bmodel%5D=suzuki-gsx-r-1000',
    'Honda CB 600F Hornet': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=honda&s%5Bmodel%5D=honda-cb-600f-hornet',
    'Honda XL 1000V Varadero': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=honda&s%5Bmodel%5D=honda-xl-1000v-varadero',
    'Honda CBR 1000RR Fireblade': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=honda&s%5Bmodel%5D=honda-cbr-1000rr-fireblade',
    'Triumph Speed Triple': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=triumph&s%5Bmodel%5D=triumph-speed-triple',
    'Ducati Scrambler': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=ducati&s%5Bmodel%5D=ducati-scrambler',
    'BMW F 650 GS': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=bmw&s%5Bmodel%5D=bmw-f-650-gs&orderby=nejlevnejsi',
    'BMW F 800 GS': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=bmw&s%5Bmodel%5D=bmw-f-800-gs&orderby=nejlevnejsi',
    'BMW R 1200 GS': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=bmw&s%5Bmodel%5D=bmw-r-1200-gs&orderby=nejlevnejsi',
    'Kawasaki ER 6N': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=kawasaki&s%5Bmodel%5D=kawasaki-er-6n&orderby=nejlevnejsi',
    'Kawasaki Versys 650': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=kawasaki&s%5Bmodel%5D=kawasaki-versys-650&orderby=nejlevnejsi',
    'Kawasaki Z 1000': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=kawasaki&s%5Bmodel%5D=kawasaki-z-1000&orderby=nejlevnejsi',
    'Yamaha FZ 1 Fazer': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=yamaha&s%5Bmodel%5D=yamaha-fz1-fazer&orderby=nejlevnejsi',
    'Yamaha FZ6 Fazer': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=yamaha&s%5Bmodel%5D=yamaha-fz6-fazer&orderby=nejlevnejsi',
    'Yamaha Yamaha XJR 1300': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=yamaha&s%5Bmodel%5D=yamaha-xjr-1300&orderby=nejlevnejsi',
    'Yamaha XV 535 Virago': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=yamaha&s%5Bmodel%5D=yamaha-xv-535-virago&orderby=nejlevnejsi',
    'Yamaha YZF-R6': 'http://www.motorkari.cz/motobazar/motorky/?scr=268&s%5Bcat%5D=2&s%5Bznacka%5D=yamaha&s%5Bmodel%5D=yamaha-yzf-r6&orderby=nejlevnejsi',
}


def get_average_price_by_years():
    today = datetime.datetime.now()
    year = today.year

    age_results = {}

    for bike, url in BIKES.items():
        logging.debug('loading data for %s', bike)
        ads = {}
        r = requests.get(url, cookies={'paging-bazar': '200'})
        if r.status_code != 200:
            break
        tree = html.fromstring(r.text)
        data = tree.cssselect('ul.list li')
        if not data:
            continue
        for ad in data:
            text = ad.text_content()
            match = re.search(u'Roèník: ([0-9]+)', text)
            if match:
                ad_year = match.group(1)
            else:
                continue

            match = re.search('Cena([0-9\s]+)Kè', text)
            if match:
                price = int(match.group(1).replace('\xa0', ''))

            ads.setdefault(ad_year, []).append(price)

        for ad_year, prices in ads.items():
            age_results.setdefault(bike, {})
            age_results[bike][year - int(ad_year)] = statistics.median(prices)
    return age_results


def main():
    # with open('bikes.json', 'r') as fp:
    #     results = json.loads(fp.read())
    results = {}

    results.update(get_average_price_by_years())
    with open('bikes.json', 'w') as fp:
        fp.write(json.dumps(results))


if __name__ == '__main__':
    logging.root.setLevel(logging.DEBUG)
    main()
