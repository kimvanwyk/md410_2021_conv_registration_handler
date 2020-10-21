""" Parse reg form from the md410 2020 convention website and upload to the central database
"""

import attr
from dateutil.parser import parse

#from md410_2020_conv_common.db import DB

import sys
sys.path.insert(0, "/home/kimv/src/md410_2020_conv_common/md410_2020_conv_common")
import db

import json
import os.path

BOOLS = (
    "first_mdc",
    "mjf_lunch",
    # "pdg_breakfast",
    # "sharks_board",
    # "golf",
    # "sight_seeing",
    # "service_project",
)



def parse_reg_form_fields(form_data, out_dir=None):
    registrees_data = [{}, {}]
    partner = form_data["partner"]
    reg_num = 0
    events = {}
    extras = {}
    for (k, v) in form_data.items():
        if k in ("timestamp",):
            t = parse(v, yearfirst=True)
        if k in ("registration_number",) and not reg_num:
            reg_num = int(v)
        if "main_" in k:
            name = k[5:]
            if name in BOOLS:
                v = bool(v)
            registrees_data[0][name] = v
        if (partner != "partner_none") and (partner in k):
            name = k.replace(f"{partner}_", "")
            if name in BOOLS:
                v = bool(v)
            registrees_data[1][name] = v
        if ("full_reg" in k):
            events["full"] = int(v if v else 0)
        if ("partial_reg" in k):
            p = int(v if v else 0)
            events[k.replace("partial_reg_", "")] = p
        if k in ("pins",):
            extras["pins"] = int(v if v else 0)
        classes = [db.LionRegistree, db.LionRegistree if partner == "partner_lion" else db.NonLionRegistree]
    registrees = []
    for (registree_data, cls) in zip(registrees_data, classes):
        if registree_data:
            registree_data["timestamp"] = t
            registree_data["title"] = ""
            registrees.append(cls(**registree_data))
    return db.RegistreeSet(reg_num, db.Events(**events), [], db.Extras(**extras), registrees)
                              

def upload_reg_form(reg_form_file):
    with open(reg_form_file, "r") as fh:
        d = json.load(fh)
    registree_set = parse_reg_form_fields(d)
    dbh = db.DB()
    dbh.save_registree_set(registree_set)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("data", help="JSON data to parse.")
    args = parser.parse_args()
    upload_reg_form(args.data)
