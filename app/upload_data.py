""" Parse reg form from the md410 2020 convention website and upload to the central database
"""

import attr
from dateutil.parser import parse

#from md410_2020_conv_common.db import DB

import sys
sys.path.insert(0, "/home/kimv/src/md410_2020_conv_common/md410_2020_conv_common")
from db import DB

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


@attr.s
class PartialReg(object):
    banquet = attr.ib(default=0)
    convention = attr.ib(default=0)
    theme = attr.ib(default=0)


@attr.s
class Registree(object):
    reg_num = attr.ib()
    timestamp = attr.ib()
    first_names = attr.ib()
    last_name = attr.ib()
    cell = attr.ib()
    email = attr.ib()
    dietary = attr.ib()
    disability = attr.ib()
    name_badge = attr.ib()
    first_mdc = attr.ib()
    mjf_lunch = attr.ib()
    # pdg_breakfast = attr.ib()
    # sharks_board = attr.ib()
    # golf = attr.ib()
    # sight_seeing = attr.ib()
    # service_project = attr.ib()
    full_reg = attr.ib(default=0)
    partial_reg = attr.ib(default=None)
    pins = attr.ib(default=0)

    def __attrs_post_init__(self):
        self.auto_name_badge = False
        if not self.name_badge:
            self.name_badge = f"{self.first_names} {self.last_name}"
            self.auto_name_badge = True


@attr.s
class LionRegistree(Registree):
    club = attr.ib(default=None)
    district = attr.ib(default=None)
    is_lion = attr.ib(default=True)

    def __attrs_post_init__(self):
        self.lion = True
        super().__attrs_post_init__()


@attr.s
class NonLionRegistree(Registree):
    partner_program = attr.ib(default=False)
    is_lion = attr.ib(default=False)

    def __attrs_post_init__(self):
        self.lion = False
        super().__attrs_post_init__()


def parse_reg_form_fields(form_data, out_dir=None):
    first_data = {}
    second_data = {}
    partner = form_data["partner"]
    reg_num = 0
    first_partial_reg = None
    second_partial_reg = None
    is_full_reg = "full" in form_data["reg_type"]
    if not is_full_reg:
        first_partial_reg = PartialReg()
        second_partial_reg = PartialReg()
    second_attendee = None
    for (k, v) in form_data.items():
        if k in ("timestamp",):
            t = parse(v, yearfirst=True)
            first_data["timestamp"] = t
            second_data["timestamp"] = t
        if k in ("registration_number",) and not reg_num:
            reg_num = int(v)
            first_data["reg_num"] = reg_num
        if "main_" in k:
            name = k[5:]
            if name in BOOLS:
                v = bool(v)
            first_data[name] = v
        if (partner != "partner_none") and (partner in k):
            name = k.replace(f"{partner}_", "")
            if name in BOOLS:
                v = bool(v)
            second_data[name] = v
        if is_full_reg and ("full_reg" in k):
            full_reg = int(v)
            if full_reg:
                first_data["full_reg"] = 1
                full_reg -= 1
            if full_reg:
                second_data["full_reg"] = full_reg
        if not is_full_reg and ("partial_reg" in k):
            p = int(v)
            if p:
                setattr(first_partial_reg, k.replace("partial_reg_", ""), 1)
                p -= 1
            if p:
                setattr(second_partial_reg, k.replace("partial_reg_", ""), p)
        if k in ("pins",):
            first_data["pins"] = int(v if v else 0)
    if first_partial_reg:
        first_data["partial_reg"] = first_partial_reg
    if partner != "partner_none":
        reg_num += 1
        second_data["reg_num"] = reg_num
        if second_partial_reg:
            second_data["partial_reg"] = second_partial_reg
    first_attendee = LionRegistree(**first_data)
    if partner != "partner_none":
        if partner == "partner_lion":
            second_attendee = LionRegistree(**second_data)
        else:
            second_attendee = NonLionRegistree(**second_data)

    return (first_attendee, second_attendee)


def upload_reg_form(reg_form_file):
    with open(reg_form_file, "r") as fh:
        d = json.load(fh)
    (first_attendee, second_attendee) = parse_reg_form_fields(d)
    db = DB()
    db.upload_registree(first_attendee)
    if second_attendee:
        db.upload_registree(second_attendee)
        db.pair_registrees(first_attendee.reg_num, second_attendee.reg_num)
    return (first_attendee, second_attendee)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("data", help="JSON data to parse.")
    args = parser.parse_args()
    upload_reg_form(args.data)
