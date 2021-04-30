#!/bin/env python3

"""
Compare cipher suites to baselines.

Authors :
  - Arthur Le Corguille
  - William Gougam
  - Adrian Kalmar
  - Alexandre Janvrin.
"""
import re
import shlex
import subprocess
from functools import partial
from importlib import resources

import click
import yaml

with resources.path("sslcompare", "anssi.yaml") as default_baseline_path:
    DEFAULT_BASELINE_PATH = default_baseline_path


@click.command()
@click.argument("url")
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "--baseline", default=DEFAULT_BASELINE_PATH, help="baseline file (yaml)."
)
def main(url, baseline, verbose=False):
    """Scan URL's cipher suites and compares it to the BASELINE.

    Cipher suites are retrieved with the testssl.sh shell script
    (https://github.com/drwetter/testssl.sh)

    Examples :
        sslcompare https://mytargetsite.com -b /path/to/baseline.yaml
        sslcompare 127.0.0.1:8080
    """
    strip_ansi = partial(re.compile(r"\x1b\[\d*m").sub, "")

    with open(baseline) as baseline_path:
        baseline_suites = yaml.safe_load(baseline_path)

    with resources.as_file(resources.files("sslcompare")) as sslcompare_path:
        with subprocess.Popen(
            shlex.split(
                f"{sslcompare_path / 'testssl.sh/testssl.sh'} -E -U {url}"
            ),
            bufsize=1,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as testssl:

            current_protocol = None
            interesting_lines = False

            for line in testssl.stdout:
                line = line.rstrip()

                if "Start" in line:
                    click.echo(line)

                elif "Done" in line:
                    click.echo(line)
                    break

                elif "Testing" in line:
                    if not (verbose or interesting_lines):
                        click.echo("")

                    click.echo(line)
                    interesting_lines = True

                elif "Cipher Suite Name (IANA/RFC)" in line:
                    click.echo(
                        f" {'Cipher Suite Name (IANA/RFC)':41} Evaluation"
                    )

                elif strip_ansi(line) in [
                    "SSLv2",
                    "SSLv3",
                    "TLS 1",
                    "TLS 1.1",
                    "TLS 1.2",
                    "TLS 1.3",
                ]:
                    current_protocol = strip_ansi(line)
                    click.echo(line)
                    continue

                elif current_protocol is not None and line != "":
                    if line == " -":
                        if current_protocol in [
                            "SSLv2",
                            "SSLv3",
                            "TLS 1",
                            "TLS 1.1",
                        ]:
                            click.echo(
                                f" {'NOT OFFERED':<41} "
                                + click.style("[RECOMMENDED]", fg="green")
                            )
                        else:
                            click.echo(f" {'NOT OFFERED':<41}")

                    else:
                        cipher_suite = line.split()[-1]

                        try:
                            click.echo(
                                f" {cipher_suite:<41} "
                                + click.style(
                                    **baseline_suites[current_protocol][
                                        cipher_suite
                                    ]
                                )
                            )

                        except KeyError:
                            click.echo(
                                f" {cipher_suite: <41} "
                                + click.style("[DEPRECATED ]", fg="red")
                            )

                elif interesting_lines or verbose:
                    click.echo(line)
