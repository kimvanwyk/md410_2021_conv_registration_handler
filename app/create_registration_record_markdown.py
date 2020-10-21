""" Create a registration record for the Lions MD410 2020 Convenrtion
from form data from the convention website
"""

import attr
import json
import os.path

#from md410_2020_conv_common.db import DB as common_db
import sys
sys.path.insert(0, "/home/kimv/src/md410_2020_conv_common/md410_2020_conv_common")
import db

EVENT_DESCRIPTIONS = {
    "full": "Full",
    "banquet": "Banquet",
    "convention": "MD410 Convention",
    "theme": "Theme Evening"
}

ORDERS = ("First", "Second")



def render_registree(registree):
    out = []
    out.append(f"* **First Name(s):** {registree.first_names}")
    out.append(f"* **Last Name:** {registree.last_name}")
    if registree.cell:
        out.append(f"* **Cell Phone:** {registree.cell}")
    if registree.email:
        out.append(f"* **Email Address:** {registree.email}")
    if registree.lion:
        out.append(f"* **Club:** {registree.club}")
        out.append(f"* **District:** {registree.district}")
    out.append(
        f"* **Dietary Requirements:** {registree.dietary if registree.dietary else 'None'}"
    )
    out.append(
        f"* **Disabilities:** {registree.disability if registree.disability else 'None'}"
    )
    if not registree.lion:
        out.append(
            f"* **Interested in a Partner's Program:** {'Yes' if registree.partner_program else 'No'}"
        )
    out.append(
        f"* **This will be the attendee's first MD Convention:** {'Yes' if registree.first_mdc else 'No'}"
    )
    out.append(
        f"* **Attendee will attend the Melvin Jones lunch:** {'Yes' if registree.mjf_lunch else 'No'}"
    )
    out.append(f"* **Details On Name Badge:** {registree.name_badge}")
    if registree.auto_name_badge:
        out.append("")
        out.append(
            f"**The name badge details were generated from the first and last names because no name badge details were supplied on the registration form. Please contact the registration team if you would like to update these details.**"
        )
    return out

def render_events(events):
    out = []
    costs = events.get_costs_per_item()
    for (event,number) in attr.asdict(events, filter=attr.filters.exclude(dict)).items():
        if number:
            out.append(
                f"* **{number} {EVENT_DESCRIPTIONS[event]} Registration{'s' if number > 1 else ''}:** R{costs[event]}"
            )
    return out


@attr.s
class Extras(object):
    pins = attr.ib()

    def __attrs_post_init__(self):
        self.attrs = ("pins",)

    def __bool__(self):
        return bool(sum([getattr(self, attr) for attr in self.attrs]))

    def render(self):
        out = []
        self.cost = 0
        for attr in self.attrs:
            a = getattr(self, attr)
            if a:
                (description, cost) = EXTRA_TYPES[attr]
                self.cost += cost * a
                out.append(
                    f"* **{a} {description}{'s' if a > 1 else ''}:** R{cost * a}"
                )
        return out


@attr.s
class RegistrationRecord(object):
    registree_set = attr.ib()
    out_dir = attr.ib(default=None)

    def __make_names(self, attr):
        self.names.append(
            f"{attr.first_names[0].lower()}_{attr.last_name.replace(' ','_').lower()}"
        )

    def __payment_details(self):
        reg_nums = "/".join(f"{r:03}" for r in self.reg_nums)
        self.out.append(f"# Payment Details {{-}}")
        self.out.append(
            f"""\

Please make all payments to this account:

* **Bank**: Nedbank
* **Account Type**: Savings Account
* **Branch Code**: 138026
* **Account Number**: 2015836799
* **Account Name**: Convention 2020

Please make EFT payments rather than cash deposits wherever possible.

Use the reference "*MDC{registree_set.reg_num}*" when making payments. 

Your registration will be finalised on the payment of a deposit of R{300 * len(self.registree_set.registrees)}{' (R300 per attendee).' if len(self.registree_set.registrees) > 1 else '.'}

Payments can be made in as many instalments as you wish, as long as full payment is received by 31 March 2020.

Please send proof of payment for any payments made to [vanwykk@gmail.com](mailto:vanwykk@gmail.com) and [david.shone.za@gmail.com](mailto:david.shone.za@gmail.com).

## Cancellations {{-}}

* If your registration is cancelled before 1 April 2020, 90% of the payments you have made will be refunded.
* Cancellations after 1 April will not be refunded as the full expenses will already have been incurred for the registration.

Thank you again for registering for the 2020 MD410 Convention.
"""
        )

    def __attrs_post_init__(self):
        self.names = []
        self.out = [f"* **Registration Number**: MDC{self.registree_set.reg_num:03}"]

        self.out.append(f"# Attendee Details - Registered on {self.registrees[0].timestamp:%d/%m/%y at %H:%M} {{-}}")
        for (n, registree) in enumerate(self.registrees, 1):
            if n == 1:
                self.out.append(f"## First Attendee {{-}}")
            else:
                self.out.append("")
                self.out.append(
                    f"## {'Lion' if registree.lion else 'Non-Lion'} Partner {{-}}"
                )
            self.out.extend(render_registree(registree))
            self.__make_names(att)
        self.names = "_".join(self.names)
        self.out.append("")
        self.out.append("## Registration Details {-}")
        self.out.append("")
        self.out.extend(self.registration.render())
        self.cost = self.registration.cost
        if self.extras:
            self.out.append("")
            self.out.append("## Extra Items {-}")
            self.out.append("")
            self.out.extend(self.extras.render())
            self.cost += self.extras.cost
        self.out.append("")
        self.out.append(f"# Total Cost: R{self.cost} {{-}}")
        self.out.append("")
        self.out.append("")
        self.__payment_details()
        self.fn = f"mdc2020_registration_{'_'.join([f'{rn:03}' for rn in self.reg_nums])}_{self.names}.txt"
        if self.out_dir:
            self.fn = os.path.join(self.out_dir, self.fn)

    def save(self):
        with open(self.fn, "w") as fh:
            fh.write("\n".join(rf.out))

def main(reg_num, out_dir, print_fn=False):
    dbh = db.DB()
    registree_set = dbh.get_registrees(reg_num)
    for registree in registree_set.registrees:
        print('\n'.join(render_registree(registree)))
        print()
    print('\n'.join(render_events(registree_set.events)))
              
    # rf.save()
    # if print_fn:
    #     print(fn)
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build MD410 2020 Convention registration record"
    )
    parser.add_argument("reg_num", type=int, help="The first reg_num to use.")
    parser.add_argument(
        "--out_dir", default="/io/", help="The directory to write output to."
    )
    parser.add_argument("--fn", action="store_true", help="Output resulting filename")
    args = parser.parse_args()

    main(args.reg_num, args.out_dir, args.fn)
