SettleUp Statistics
===================

Transforms exported SQLite database of the mobile app [SettleUp](http://www.settleup.info/) for a chosen group into CSV for
evaluating tracked expenses.
Outputs a CSV on stdout that has one row per payment and the following columns:

1. purpose of payment
2. date of payment
3. full monetary amount of payment in output currency (chosen by --currency)
4. one column for each member associated with this group, detailing his share of the payment amount


Features
--------
- adds up split payments
- considers uneven payment splits
- the output currency can be chose, but must be one of the currencies available in the app


Usage
-----
```
usage: stats.py [-h] --sqlite-file SQLITE_FILE --group-name GROUP_NAME
                --currency CURRENCY

arguments:
  --sqlite-file SQLITE_FILE
                        the sqlite file that was exported from SettleUp
  --group-name GROUP_NAME
                        the name of the SettleUp group that shall be regarded
  --currency CURRENCY   the currency code for the monetary amounts in the
                        output CSV
```