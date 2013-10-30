#!/usr/bin/python3
__author__ = 'florian'

import sqlite3
import csv
import sys
import datetime
import argparse

# PARSE ARGS
parser = argparse.ArgumentParser(description="Transforms exported SQLite database of the mobile app SettleUp "
                                             "into CSV for evaluating tracked expenses.")
parser.add_argument('--sqlite-file', required=True,
                    help='the sqlite file that was exported from SettleUp', type=argparse.FileType('rb'))
parser.add_argument('--group-name', required=True,
                    help='the name of the SettleUp group that shall be regarded')
parser.add_argument('--currency', required=True,
                    help='the currency code for the monetary amounts in the output CSV')
args = parser.parse_args()

groupName = args.group_name

outputCurrency = args.currency


# OPEN SQLITE FILE
conn = sqlite3.connect(args.sqlite_file.name)
# be able to access rows as dictionaries
conn.row_factory = sqlite3.Row


# GET CURRENCIES
mcu = conn.cursor()
mcu.execute("""
   SELECT code, exchange_rate, exchange_code
   FROM currencies;
""")

currencies = [{k: c[k] for k in c.keys()} for c in mcu.fetchall()]

if not list(filter(lambda c: c['code'] == outputCurrency, currencies)):
    raise ValueError(
        "output currency {} not available, only {}".format(outputCurrency, list(map(lambda c: c['code'], currencies))))

outputCurrencyExchangeRate, = filter(lambda c: c['code'] == outputCurrency, currencies)
outputCurrencyExchangeRate = outputCurrencyExchangeRate['exchange_rate']

exchangeRateInOutputCurrency = {}
for c in currencies:
    exchangeRateInOutputCurrency[c['code']] = c['exchange_rate'] / outputCurrencyExchangeRate


# GET MEMBERS
mc = conn.cursor()

mc.execute("""
SELECT m._id, m.name
FROM members AS m INNER JOIN groups AS g ON m.group_id = g._id
WHERE g.name = ?""", [groupName])

members = {}

for m in mc:
    members[m['_id']] = m['name']

if not members:
    raise argparse.ArgumentError('no members for group ' + groupName)


# WRITE CSV HEADERS
writer = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['purpose', 'date', 'full amount ({})'.format(outputCurrency)] +
                list(map(lambda x: '{} ({})'.format(x, outputCurrency), list(members.values()))))


# FOR EACH PAYMENT, TRANSFORM IT, AND WRITE CSV LINE
pc = conn.cursor()

pc.execute("""
SELECT p._id, p.for_who, p.amount, p.weights, p.purpose, p.created, p.currency, p.transfer
FROM payments AS p INNER JOIN groups AS g ON p.group_id = g._id
WHERE g.name = ?""", [groupName])

for payment in pc:
    # omit transfers, they are not expenses
    if payment['transfer'] == 1:
        continue

    purpose = payment['purpose']

    date = datetime.datetime.fromtimestamp(int(payment['created']) / 1000).strftime('%Y-%m-%d %H:%M:%S')

    # sum amount since multiple people could have paid
    amount = sum([float(i) for i in payment['amount'].split(' ')])
    amountInOutputCurrency = amount / exchangeRateInOutputCurrency[payment['currency']]

    forWho = [int(i) for i in payment['for_who'].split(' ')]
    weights = [float(i) for i in payment['weights'].split(' ')]

    howMuchForWho = {m: 0.0 for m in members.keys()}

    for i, benefitor in enumerate(forWho):
        howMuchForWho[benefitor] = weights[i] / sum(weights) * amountInOutputCurrency

    writer.writerow([purpose, date, amountInOutputCurrency] +
                    list(howMuchForWho.values()))
