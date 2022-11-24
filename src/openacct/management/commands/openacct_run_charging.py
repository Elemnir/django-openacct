#!/usr/bin/env python3
import datetime
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q

from openacct.models import Account, Service, Transaction

logger = logging.getLogger(__name__)


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
        parser.add_argument("--names-contain", action="store_true",
            help="If set, names passed to --services, --projects, and --accounts will be treated as substrings instead of exact matches"
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
        use_contains = kwargs["names-contain"]
        overwrite = kwargs["force-recalculation"]

        # Collect relevant services
        q = None
        if kwargs["systems"] is not None:
            for system in kwargs["systems"].split(","):
                if q is None:
                    if use_contains:
                        q = Q(system__name__icontains=system)
                    else:
                        q = Q(system__name=system)
                else:
                    if use_contains:
                        q |= Q(system__name__icontains=system)
                    else:
                        q |= Q(system__name=system)
        elif kwargs["services"] is not None:
            for service in kwargs["services"].split(","):
                if q is None:
                    if use_contains:
                        q = Q(name__icontains=service)
                    else:
                        q = Q(name=service)
                else:
                    if use_contains:
                        q |= Q(name__icontains=service)
                    else:
                        q |= Q(name=service)

        services = "ANY"
        if q is not None:
            services = Service.objects.filter(q, active=True)

        # Collect relevant accounts
        q = None
        if kwargs["projects"] is not None:
            for project in kwargs["projects"].split(","):
                if q is None:
                    if use_contains:
                        q = Q(project__name__icontains=project)
                    else:
                        q = Q(project__name=project)
                else:
                    if use_contains:
                        q |= Q(project__name__icontains=project)
                    else:
                        q |= Q(project__name=project)
        elif kwargs["accounts"] is not None:
            for account in kwargs["accounts"].split(","):
                if q is None:
                    if use_contains:
                        q = Q(name__icontains=account)
                    else:
                        q = Q(name=account)
                else:
                    if use_contains:
                        q |= Q(name__icontains=account)
                    else:
                        q |= Q(name=account)

        accounts = "ANY"
        if q is not None:
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
