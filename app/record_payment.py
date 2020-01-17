""" Record a registration payment
"""

from datetime import datetime
from decimal import Decimal, getcontext
import os.path

from md410_2020_conv_common.db import DB

import attr
import sqlalchemy as sa

getcontext().prec = 20
TWOPLACES = Decimal(10) ** -2


def record_payment(reg_num, amount, timestamp):
    db = DB()
    db.set_reg_nums(reg_num)
    db.record_payment(amount, timestamp)


if __name__ == "__main__":
    import inquirer

    dt = datetime.now()

    questions = [
        inquirer.Text("reg_num", "Registration Number"),
        inquirer.Text("amount", "Payment Amount"),
        inquirer.Text("timestamp", "Timestamp", default=dt.strftime("%y/%m/%d %H:%M")),
    ]

    answers = inquirer.prompt(questions)
    record_payment(
        int(answers["reg_num"]),
        Decimal(answers["amount"]),
        datetime.strptime(answers["timestamp"], "%y/%m/%d %H:%M"),
    )
