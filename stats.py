__author__ = 'florian'

import sqlite3
import csv
import sys

groupName = 'Rasselbande'
outputCurrency = 'USD'

conn = sqlite3.connect("data/export.sqlite")
conn.row_factory = sqlite3.Row

# GET CURRENCIES
mcu = conn.cursor()
mcu.execute("""
   SELECT code, exchange_rate, exchange_code
   FROM currencies;
""")

currencies = [{k: c[k] for k in c.keys()} for c in mcu.fetchall()]

if not list(filter(lambda c: c['code'] == outputCurrency, currencies)):
    raise ValueError("output currency {} not available, only {}".format(outputCurrency, list(map(lambda c: c['code'], currencies))))

# TODO: continue here
exchangeRateInOutputCurrency = {}


# GET MEMBERS
mc = conn.cursor()

mc.execute("""
SELECT m._id, m.name
FROM members AS m INNER JOIN groups AS g ON m.group_id = g._id
WHERE g.name = ?""", [groupName])

members = {}

for m in mc:
    members[m['_id']] = m['name']

print(members)

# CSV HEADERS

#with open('payments.csv', 'wb') as csvFile:
writer = csv.writer(sys.stdout, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['purpose', 'date'] + list(members.values()))


# GET PAYMENTS
pc = conn.cursor()

pc.execute('''
SELECT p._id, p.for_who, p.amount, p.weights, p.purpose, p.created, p.currency, p.transfer
FROM payments AS p INNER JOIN groups AS g ON p.group_id = g._id
WHERE g.name = ?''', [groupName])


for payment in pc:
    # omit transfers, they are not expenses
    if payment['transfer'] == 1:
        #print(payment['_id'], "TRANSFER")
        continue

    howMuchForWho = {m: 0.0 for m in members.keys()}

    purpose = payment['purpose']
    # TODO: transform timestamp into something useful
    date = payment['created']

    forWho = [int(i) for i in payment['for_who'].split(' ')]
    weights = [float(i) for i in payment['weights'].split(' ')]
    # sum amount since multiple people could have paid
    amount = sum([float(i) for i in payment['amount'].split(' ')])
    amountInOutputCurrency = amount * exchangeRateInOutputCurrency[payment['currency']]

    for i,benefitor in enumerate(forWho):
        howMuchForWho[benefitor] = weights[i] / sum(weights) * amountInOutputCurrency

    writer.writerow([purpose, date] + list(howMuchForWho.values()))
