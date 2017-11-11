import datetime
import itertools
import json
import logging
import statistics

import requests

CARS = {
    'Skoda Octavia': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=93&model=705&nocache=535',
    'Skoda Superb': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=93&model=708&nocache=535',
    'Skoda Fabia': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=93&model=707&nocache=535',
    'VW Golf': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=103&model=759&nocache=862',
    'VW Passat': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=103&model=762&nocache=862',
    'BMW 3': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=5&model=39&nocache=317',
    'Ford Mondeo': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=24&model=190&nocache=627',
    'Ford Focus': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=24&model=197&nocache=627',
    'Volvo v40': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=106&model=790&nocache=982',
    'Volvo v60': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=106&model=5779&nocache=204',
    'Citroen C4 Picasso': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=13&model=1323&nocache=204',
    'Honda Civic': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=28&model=226&nocache=204',
    'Hyundai i30': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=31&model=1376&nocache=204',
    'Peugeot 308': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=70&model=1416&nocache=204',
    'Renault Megane': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=78&model=612&nocache=204',
    'Seat Leon': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=86&model=668&nocache=204',
    'Subaru Forester': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=88&model=679&nocache=204',
    'Toyota Avensis': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=99&model=736&nocache=204',

}


def get_average_price_by_years():
    today = datetime.datetime.now()
    year = today.year

    age_results = {}

    for car, url in CARS.items():
        logging.debug('loading data for %s', car)
        ads = {}
        for page in itertools.count():
            r = requests.get(url.format(page))
            if r.status_code != 200:
                break
            data = r.json()
            if not data.get('advert'):
                break
            for ad in data['advert']:
                if not ad.get('advert_run_date'):
                    continue
                ads.setdefault(ad['advert_run_date'], []).append(ad['advert_price_total'])
            if page % 10 == 0:
                logging.debug('%d pages loaded', page)

        for ad_year, prices in ads.items():
            age_results.setdefault(car, {})
            age_results[car][year - int(ad_year)] = statistics.median(prices)
    return age_results


def main():
    with open('result.json', 'r') as fp:
        results = json.loads(fp.read())

    results.update(get_average_price_by_years())
    with open('result.json', 'w') as fp:
        fp.write(json.dumps(results))


if __name__ == '__main__':
    logging.root.setLevel(logging.DEBUG)
    main()
