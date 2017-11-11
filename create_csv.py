import argparse
import csv
import json


def main(args):
    result_file = args.file.replace('.json', '.csv')

    with open(args.file, 'r') as fp, open(result_file, 'w') as csvfile:
        data = json.loads(fp.read())

        writer = csv.writer(csvfile)
        writer.writerow(['Age'] + list(data.keys()))

        for age in range(30):
            row = [age]
            for item in data:
                if data[item].get(str(age)):
                    row.append(int(data[item][str(age)]))
                else:
                    row.append('')
            writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Price by age')
    parser.add_argument('file', default='result.json')
    main(parser.parse_args())
