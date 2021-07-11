#!/bin/env python3

"""
Compare cipher suites to baselines.

Authors :
  - Arthur Le Corguille
  - William Gougam
  - Adrian Kalmar
  - Alexandre Janvrin.
"""
import json
import re
import subprocess
from sys import argv


def style(text, fg):
    colors = {"red": 31, "yellow": 33, "green": 32}
    return "".join(
        [
            f"\x1b[{colors[fg]};1m",
            text,
            "\x1b[0m",
        ]
    )


def main(url, verbose=False):
    """Scan URL's cipher suites and compares it to the BASELINE.

    Cipher suites are retrieved with the testssl.sh shell script
    (https://github.com/drwetter/testssl.sh)

    Examples :
        sslcompare https://mytargetsite.com -b /path/to/baseline.yaml
        sslcompare 127.0.0.1:8080
    """
    strip_ansi = re.compile(r"\x1b\[\d*m").sub

    with open("anssi.json") as baseline_path:
        baseline_suites = json.load(baseline_path)

    with subprocess.Popen(
        ["./testssl.sh/testssl.sh", "-E", "-U", url],
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
                print(line)

            elif "Done" in line:
                print(line)
                break

            elif "Testing" in line:
                if not (verbose or interesting_lines):
                    print("")

                print(line)
                interesting_lines = True

            elif "Cipher Suite Name (IANA/RFC)" in line:
                print(f" {'Cipher Suite Name (IANA/RFC)':41} Evaluation")

            elif strip_ansi("", line) in [
                "SSLv2",
                "SSLv3",
                "TLS 1",
                "TLS 1.1",
                "TLS 1.2",
                "TLS 1.3",
            ]:
                current_protocol = strip_ansi("", line)
                print(line)
                continue

            elif current_protocol is not None and line != "":
                if line == " -":
                    if current_protocol in [
                        "SSLv2",
                        "SSLv3",
                        "TLS 1",
                        "TLS 1.1",
                    ]:
                        print(
                            f" {'NOT OFFERED':<41} "
                            + style("[RECOMMENDED]", fg="green")
                        )
                    else:
                        print(f" {'NOT OFFERED':<41}")

                else:
                    cipher_suite = line.split()[-1]

                    try:
                        print(
                            f" {cipher_suite:<41} "
                            + style(
                                **baseline_suites[current_protocol][
                                    cipher_suite
                                ]
                            )
                        )

                    except KeyError:
                        print(
                            f" {cipher_suite: <41} "
                            + style("[DEPRECATED ]", fg="red")
                        )

            elif interesting_lines or verbose:
                print(line)


if __name__ == "__main__":
    main(argv[1])
