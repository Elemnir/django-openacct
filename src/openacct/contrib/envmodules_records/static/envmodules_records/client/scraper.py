#!/usr/bin/env python3

import argparse
import configparser
import datetime
import json
import os
import re

import requests


PATTERNS = {
    "cmd": (
        r"(?P<when>\w{3}\s+\d+ \d{2}:\d{2}:\d{2}) (?P<host>\S+) "
        + r"(?P<service>\S+)\[\d+\]: (?P<type>module-cmd) (?P<data>{.*})$"
    ),
    "event": (
        r"(?P<when>\w{3}\s+\d+ \d{2}:\d{2}:\d{2}) (?P<host>\S+) "
        + r"(?P<service>\S+)\[\d+\]: (?P<type>module-event) (?P<data>{.*})$"
    ),
}


class ApiClient:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.getenv("API_CONFIG_PATH", "api.cfg"))
        self.url_prefix = config["ApiServer"]["url_prefix"]
        self.token = config["ApiServer"]["token"]

    def send(self, endpoint: str, payload: dict):
        resp = requests.post(
            os.path.join(self.url_prefix, endpoint),
            data=payload,
            headers={"Authorization": "Token " + self.token},
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise RuntimeError(f"Server responded: {resp.status_code}")


def scan_file(path, patterns=["cmd", "event"]):
    with open(path) as f:
        for line in f:
            for label in patterns:
                m = re.search(PATTERNS[label], line.rstrip())
                if m:
                    yield m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="")
    parser.add_argument(
        "--year",
        required=False,
        default=datetime.date.today().year,
        help="Set for the year the log was generated. Defaults to the current year",
    )

    args = parser.parse_args()
    client = ApiClient()
    for m in scan_file(args.path):
        payload = {
            "when": datetime.datetime.strptime(
                " ".join([str(args.year), m.group("when")]),
                "%Y %b %d %H:%M:%S",
            ),
            "host": m.group("host"),
        }

        data_str = m.group("data")
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"Skipping bad JSON object: {data_str}")
            continue

        payload.update(data)
        if m.group("type") == "module-cmd":
            client.send("/record_command/", payload)
        elif m.group("type") == "module-event":
            client.send("/record_event/", payload)
        else:
            print("Unexpected regex match with log type: " + m.group("type"))
