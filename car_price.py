import datetime
import itertools
import json
import logging
import statistics

import requests

CARS = {
    'skoda octavia': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=93&model=705&nocache=535',
    'vw golf': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=103&model=759&nocache=862',
    'vw passat': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=103&model=762&nocache=862',
    'bmw 3': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=5&model=39&nocache=317',
    'bmw 5': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=5&model=40&nocache=317',
    'ford mondeo': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=24&model=190&nocache=627',
    'ford focus': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=24&model=197&nocache=627',
    'volvo v40': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=106&model=790&nocache=982',
    'volvo v60': 'https://www.sauto.cz/hledani?ajax=2&page={}&condition=4&condition=2&condition=1&category=1&manufacturer=106&model=5779&nocache=204',
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
