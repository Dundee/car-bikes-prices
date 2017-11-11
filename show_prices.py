import argparse
from collections import OrderedDict
import json

import matplotlib.pyplot as plt


def main(args):
    plt.title("Price by age")
    plt.xlabel('age')
    plt.ylabel('price')

    with open(args.file, 'r') as fp:
        data = json.loads(fp.read())

        for item in data:
            prices = OrderedDict(sorted(data[item].items(), key=lambda item: int(item[0])))

            plt.plot(
                [int(age) for age in prices.keys()],
                [int(price) for price in prices.values()],
                label=item,
            )

    plt.legend()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Price by age')
    parser.add_argument('file', default='result.json')
    main(parser.parse_args())
