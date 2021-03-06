import attr
import json
import os.path

from md410_2021_conv_common import db, constants

DESCRIPTIONS = {
    "full": "Full",
    "district_convention": "District Convention",
    "banquet": "Banquet",
    "md_convention": "MD410 Convention",
    "theme": "Theme Evening",
    "pins": "Convention Pin",
}


@attr.s
class RegistreeSetRenderer(object):
    registree_set = attr.ib()
    out_dir = attr.ib(default=None)

    def __make_names(self, attr):
        self.names.append(
            f"{attr.first_names[0].lower()}_{attr.last_name.replace(' ','_').lower()}"
        )

    def __payment_details(self):
        self.out.append(f"\\newpage\n# Payment Details {{-}}")
        deposit_explanation = (
            f" (R{constants.DEPOSIT} per attendee)."
            if len(self.registree_set.registrees) > 1
            else "."
        )
        self.out.append(
            f"""\

Please make all payments to this account:

* **Bank**: Nedbank
* **Account Type**: Savings Account
* **Branch Code**: 138026
* **Account Number**: 2015836799
* **Account Name**: Convention 2020

It was cost-effective to retain the account set up for the 2020 MD Convention, so the account name is still "Convention 2020".

Please make EFT payments rather than cash deposits wherever possible.

Use the reference "*{self.registree_set.reg_num_text}*" when making payments. 

Your registration will be finalised on the payment of a deposit of R{self.registree_set.deposit}{deposit_explanation}

Payments can be made in as many instalments as you wish, as long as full payment is received by {constants.FULL_PAYMENT_DEADLINE:%d %B %Y}.

Please send proof of payment for any payments made to [vanwykk@gmail.com](mailto:vanwykk@gmail.com) and [david.shone.za@gmail.com](mailto:david.shone.za@gmail.com).

## Cancellations {{-}}

* If your registration is cancelled before {constants.CANCELLATION_DEADLINE:%d %B %Y}, 90% of the payments you have made will be refunded.
* Cancellations after {constants.CANCELLATION_DEADLINE:%d %B} will not be refunded as the full expenses will already have been incurred for the registration.

Thank you again for registering for the 2021 MD410 Convention.
"""
        )

    def __attrs_post_init__(self):
        self.names = []
        self.out = [
            f"# Registration Number: {self.registree_set.reg_num_text} {{-}}",
        ]

        self.out.append(
            f"# Attendee Details - Registered on {self.registree_set.registrees[0].timestamp:%d/%m/%y at %H:%M} {{-}}"
        )
        for (n, registree) in enumerate(self.registree_set.registrees, 1):
            self.registree = registree
            if n == 1:
                self.out.append("")
                self.out.append(f"## First Attendee {{-}}")
            else:
                self.out.append("")
                self.out.append(
                    f"## {'Lion' if self.registree.lion else 'Non-Lion'} Partner {{-}}"
                )
            self.render_registree()
            self.__make_names(registree)
        self.names = "_".join(self.names)
        self.out.append("")
        self.out.append("## Registration Details {-}")
        self.out.append("")
        self.render_events()
        if self.registree_set.extras.cost:
            self.out.append("")
            self.out.append("## Extra Items {-}")
            self.out.append("")
            self.render_extras()
        self.out.append("")
        self.out.append(f"# Total Cost: R{self.registree_set.cost} {{-}}")
        if self.registree_set.paid:
            self.out.append("")
            self.out.append("")
            self.out.append(
                f"Our records indicate that you paid R{self.registree_set.paid} towards the 2020 MD Convention, which the organising committee has held in the conference account. If these records are incorrect please contact the registration team urgently."
            )
            if self.registree_set.paid_in_full:
                self.out.append("")
                self.out.append(
                    "**The payments you made for the 2020 MD Convention have covered your 2021 amount in full.**"
                )
            else:
                self.out.append("")
                self.out.append(f"# Still Owed: R{self.registree_set.still_owed} {{-}}")
        self.out.append("")
        self.out.append("")
        self.__payment_details()
        self.fn = (
            f"mdc2021_registration_{self.registree_set.reg_num:003}_{self.names}.txt"
        )
        if self.out_dir:
            self.fn = os.path.join(self.out_dir, self.fn)

    def render_registree(self):
        self.out.append(f"* **First Name(s):** {self.registree.first_names}")
        self.out.append(f"* **Last Name:** {self.registree.last_name}")
        if self.registree.cell:
            self.out.append(f"* **Cell Phone:** {self.registree.cell}")
        if self.registree.email:
            self.out.append(f"* **Email Address:** {self.registree.email}")
        if self.registree.lion:
            self.out.append(f"* **Club:** {self.registree.club}")
            self.out.append(f"* **District:** {self.registree.district}")
        self.out.append(
            f"* **Dietary Requirements:** {self.registree.dietary if self.registree.dietary else 'None'}"
        )
        self.out.append(
            f"* **Disabilities:** {self.registree.disability if self.registree.disability else 'None'}"
        )
        if not self.registree.lion:
            self.out.append(
                f"* **Interested in a Partner's Program:** {'Yes' if self.registree.partner_program else 'No'}"
            )
        self.out.append(
            f"* **This will be the attendee's first MD Convention:** {'Yes' if self.registree.first_mdc else 'No'}"
        )
        self.out.append(
            f"* **Attendee will attend the Melvin Jones lunch:** {'Yes' if self.registree.mjf_lunch else 'No'}"
        )
        self.out.append(
            f"* **Attendee will attend the PDGs Dinner:** {'Yes' if self.registree.pdg_dinner else 'No'}"
        )
        self.out.append(f"* **Details On Name Badge:** {self.registree.name_badge}")
        if self.registree.auto_name_badge:
            self.out.append("")
            self.out.append(
                f"**The name badge details were generated from the first and last names because no name badge details were supplied on the registration form. Please contact the registration team if you would like to update these details.**"
            )

    def render_events(self):
        costs = self.registree_set.events.get_costs_per_item()
        for (event, number) in attr.asdict(
            self.registree_set.events, filter=attr.filters.exclude(dict)
        ).items():
            if number:
                self.out.append(
                    f"* **{number} {DESCRIPTIONS[event]} Registration{'s' if number > 1 else ''}:** R{costs[event]}"
                )

    def render_extras(self):
        costs = self.registree_set.extras.get_costs_per_item()
        for (extra, number) in attr.asdict(
            self.registree_set.extras, filter=attr.filters.exclude(dict)
        ).items():
            if number:
                self.out.append(
                    f"* **{number} {DESCRIPTIONS[extra]}{'s' if number > 1 else ''}:** R{costs[extra]}"
                )

    def save(self):
        with open(self.fn, "w") as fh:
            fh.write("\n".join(self.out))


def main(reg_num=None, registree_set=None, out_dir="."):
    if not registree_set:
        if reg_num is not None:
            dbh = db.DB()
            registree_set = dbh.get_registrees(reg_num)
        else:
            raise ValueError(
                "Either a reg num to look up or a RegistreeSet should be provided"
            )
    renderer = RegistreeSetRenderer(registree_set, out_dir)

    renderer.save()
    return renderer.fn


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build MD410 2021 Convention registration record"
    )
    parser.add_argument("reg_num", type=int, help="The first reg_num to use.")
    parser.add_argument(
        "--out_dir", default=".", help="The directory to write output to."
    )
    parser.add_argument("--fn", action="store_true", help="Output resulting filename")
    args = parser.parse_args()

    main(reg_num=args.reg_num, out_dir=args.out_dir, print_fn=args.fn)
