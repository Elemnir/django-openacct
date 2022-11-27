#!/usr/bin/env python3
import datetime
import logging

from typing import Literal

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q

from openacct.models import Account, Service, Transaction

logger = logging.getLogger(__name__)


def translate_names_to_filters(
    names: list[str],
    prefix: str,
    scheme: Literal["exact", "startswith", "contains"]
) -> Q:
    """Given a list of names, translate them into a Q representing that set"""
    key = prefix + {
        "exact": "", "startswith": "__startswith", "contains": "__icontains"
    }[scheme]
    q = Q()
    for name in names:
        q |= Q(**{key: name})
    return q


class Command(BaseCommand):
    help = "Calculate charge amounts for a selection of transactions"

    def add_arguments(self, parser):
        parser.add_argument("--start", required=True,
            type=datetime.datetime.fromisoformat,
            help="(Required) ISO-formatted timestamp to be the start of the selection window"
        )
        parser.add_argument("--end", required=True,
            type=datetime.datetime.fromisoformat,
            help="(Required) ISO-formatted timestamp to be the end of the selection window"
        )
        parser.add_argument("--systems", required=False, default=None,
            help="Comma separated list of system names for selecting transactions. Cannot use with --services"
        )
        parser.add_argument("--services", required=False, default=None,
            help="Comma separated list of service names for selecting transactions. Cannot use with --systems"
        )
        parser.add_argument("--projects", required=False, default=None,
            help="Comma separated list of project names for selecting transactions. Cannot use with --accounts"
        )
        parser.add_argument("--accounts", required=False, default=None,
            help="Comma separated list of account names for selecting transactions. Cannot use with --projects"
        )
        parser.add_argument("--match-scheme", required=False, default="exact",
            choices=["exact", "startswith", "contains"],
            help="Choose whether names are matched exactly, when the start of the name matches, or if the substring appears anywhere in the name"
        )
        parser.add_argument("--force-recalculation", action="store_true",
            help="If set, transactions which already have a calculated charge value will be recalculated"
        )
        parser.add_argument("--discount", required=False, default=0.0, type=float,
            help="Apply a discount to the services' charge rates. Must be a float in the range [0.0, 1.0)"
        )
        parser.add_argument("--auto-confirm", action="store_true",
            help="If set, disable pauses for confirmation"
        )

    def handle(self, *args, **kwargs):
        if kwargs["start"] > kwargs["end"]:
            raise CommandError("Start must be before End")
        if kwargs["systems"] is not None and kwargs["services"] is not None:
            raise CommandError("May only specify systems or services, but not both")
        if kwargs["projects"] is not None and kwargs["accounts"] is not None:
            raise CommandError("May only specify projects or accounts, but not both")
        if kwargs["discount"] >= 1.0 or kwargs["discount"] < 0.0:
            raise CommandError("Discount must be within the range [0.0, 1.0)")

        charge_multiplier = 1.0 - kwargs["discount"]
        start_time = kwargs["start"]
        end_time = kwargs["end"]
        overwrite = kwargs["force-recalculation"]
        scheme = kwargs["match-scheme"]

        # Collect relevant services
        services = "ANY"
        if kwargs["systems"] is not None:
            q = translate_names_to_filters(
                kwargs["systems"].split(","), "system__name", scheme
            )
            services = Service.objects.filter(q, active=True)
        elif kwargs["services"] is not None:
            q = translate_names_to_filters(
                kwargs["services"].split(","), "name", scheme
            )
            services = Service.objects.filter(q, active=True)

        # Collect relevant accounts
        accounts = "ANY"
        if kwargs["projects"] is not None:
            q = translate_names_to_filters(
                kwargs["projects"].split(","), "project__name", scheme
            )
            accounts = Account.objects.filter(q, active=True)
        elif kwargs["accounts"] is not None:
            q = translate_names_to_filters(
                kwargs["accounts"].split(","), "name", scheme
            )
            accounts = Account.objects.filter(q, active=True)

        if not kwargs["auto-confirm"]:
            print("Charging transactions with the following:\n")
            print(f"\tTime Window: {start_time.isoformat} - {end_time.isoformat}")
            print(f"\tServices: {services}")
            print(f"\tAccounts: {accounts}")
            print(f"\tOverwrite Non-Zero Charges: {overwrite}")
            print(f"\tService Charge-Rate Multiplier: {charge_multiplier}")
            input("\nHit Enter to continue...")

        transactions = Transaction.objects.filter(
            active=True, created__gte=start_time, created__lte=end_time
        )
        if services != "ANY":
            transactions.filter(service__in=services)
        if accounts != "ANY":
            transactions.filter(account__in=accounts)
        if not overwrite:
            transactions.filter(amt_charged=0.0)

        if not kwargs["auto-confirm"]:
            count = transactions.count()
            print(f"Selection returned {count} transactions.")
            input("\nHit Enter to apply charging...")

        transactions.update(amt_charged=F("amt_used") * F("service__charge_rate") * charge_multiplier)
