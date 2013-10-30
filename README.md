SettleUp Statistics
===================

Transforms exported SQLite database of the mobile app SettleUp into CSV for
evaluating tracked expenses.


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