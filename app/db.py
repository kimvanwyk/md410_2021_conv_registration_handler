from decimal import Decimal, getcontext

import attr
import sqlalchemy as sa

getcontext().prec = 20
TWOPLACES = Decimal(10) ** -2

TABLES = {
    "registree": ("md410_2020_conv", "registree"),
    "registree_pair": ("md410_2020_conv", "registree_pair"),
    "payment": ("md410_2020_conv", "payment")
}

@attr.s
class Registree(object):
    reg_num = attr.ib()
    first_names = attr.ib()
    last_name = attr.ib()
    cell = attr.ib()
    email = attr.ib()


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

    def get_registrees(self, reg_num):
        self.set_reg_nums(reg_num)
        tr = self.tables["registree"]
        res = self.engine.execute(sa.select([tr.c.reg_num, tr.c.first_names, tr.c.last_name, tr.c.cell, tr.c.email],
                                            tr.c.reg_num.in_(self.reg_nums))).fetchall()
        registrees = []
        for r in res:
            registrees.append(Registree(*r))
        return registrees

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

