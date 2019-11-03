""" Obtain a reg form record for a given reg number and provide email steps
"""

import attr

import s3

import sqlalchemy as sa

TABLES = {
    "registree": ("md410_2020_conv", "registree"),
    "registree_pair": ("md410_2020_conv", "registree_pair"),
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
        tp = self.tables["registree_pair"]
        res = self.engine.execute(sa.select([tp.c.first_reg_num, tp.c.second_reg_num],
                                            sa.or_(tp.c.first_reg_num == reg_num,
                                                   tp.c.second_reg_num == reg_num))).fetchone()
        if res:
            self.reg_nums = [res[0], res[1]]
        else:
            self.reg_nums = [reg_num]

        tr = self.tables["registree"]
        res = self.engine.execute(sa.select([tr.c.reg_num, tr.c.first_names, tr.c.last_name, tr.c.cell, tr.c.email],
                                            tr.c.reg_num.in_(self.reg_nums))).fetchall()
        registrees = []
        for r in res:
            registrees.append(Registree(*r))
        return registrees


def send_email(reg_num):
    s = s3.S3(reg_num)
    s.download_data_file()

    db = DB()
    registrees = db.get_registrees(args.reg_num)
    print(registrees)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "reg_num", type=int, help="Registration number"
    )
    args = parser.parse_args()
    send_email(args.reg_num)
