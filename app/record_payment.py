""" Record a registration payment
"""

from datetime import datetime
from decimal import Decimal, getcontext
import os.path

import attr
import sqlalchemy as sa

getcontext().prec = 20
TWOPLACES = Decimal(10) ** -2

TABLES = {
    "payment": ("md410_2020_conv", "payment"),
    "registree_pair": ("md410_2020_conv", "registree_pair"),
}

@attr.s
class DB(object):
    """ Handle postgres database interaction
    """

    host = attr.ib(default="localhost")
    port = attr.ib(default=5432)
    user = attr.ib(default="postgres")
    dbname = attr.ib(default="postgres")
    debug = attr.ib(default=False)

    def __attrs_post_init__(self):
        self.engine = sa.create_engine(
            f"postgresql+psycopg2://{self.user}@{self.host}/{self.dbname}"
        )
        md = sa.MetaData()
        md.bind = self.engine
        self.engine.autocommit = True
        self.tables = {}
        for (k, (schema, name)) in TABLES.items():
            self.tables[k] = sa.Table(name, md, autoload=True, schema=schema)
        self.reg_nums = []

    def set_reg_nums(self, reg_num):
        tp = self.tables["registree_pair"]
        res = self.engine.execute(sa.select([tp.c.first_reg_num, tp.c.second_reg_num],
                                            sa.or_(tp.c.first_reg_num == reg_num,
                                                   tp.c.second_reg_num == reg_num))).fetchone()
        if res:
            self.reg_nums = [res[0], res[1]]
        else:
            self.reg_nums = [reg_num]

    def record_payment(self, amount, timestamp):
        tp = self.tables['payment']
        amt = Decimal(amount).quantize(TWOPLACES) / (len(self.reg_nums))
        for rn in self.reg_nums:
            d = {'timestamp': timestamp,
                 'reg_num': rn,
                 'amount': amt
            }
            res = self.engine.execute(tp.insert(d))

def record_payment(reg_num, amount, timestamp):
    db = DB()
    db.set_reg_nums(reg_num)
    db.record_payment(amount, timestamp)

if __name__ == '__main__':
    import inquirer
    dt = datetime.now()

    questions=[
        inquirer.Text('reg_num', 'Registration Number'),
        inquirer.Text('amount', 'Payment Amount'),
        inquirer.Text('timestamp', 'Timestamp', default=dt.strftime("%y/%m/%d %H:%M"))]

    answers = inquirer.prompt(questions)
    record_payment(int(answers['reg_num']), Decimal(answers['amount']), datetime.strptime(answers['timestamp'], "%y/%m/%d %H:%M"))
