from argparse import ArgumentParser

from app.asap import (
    ASAP,
    InvalidASAPFile,
)
from app.output_formats import ASAPHTMLOutput


def main():
    parser = ArgumentParser(prog="cli")

    # File path to ASAP source file
    parser.add_argument(
        "asap_source_filepath",
        help="ASAP filepath"
    )

    # Personal Health Information is redacted by default in the output, -u outputs PHI
    parser.add_argument(
        "-u",
        "--unsafe-phi-display",
        dest="unsafe_phi_display",
        default=False,
        required=False,
        action="store_true",
        help="If set, do not redact PHI in the output.  Default is to redact PHI."
    )

    args = parser.parse_args()

    print("Opening: " + args.asap_source_filepath)
    try:
        with open(args.asap_source_filepath, "r") as my_file:
            asap = ASAP(my_file.read())
    except InvalidASAPFile:
        print(
            f"File {args.filepath} is not an ASAP file.  File must be text and begin with an ASAP header."
        )

    # Print basic stats
    asap.analyze()

    # Output HTML format
    html = ASAPHTMLOutput(unsafe_phi_display=args.unsafe_phi_display)
    print("Outputting ")
    with open("asap_report.html", "w") as text_file:
        text_file.write(html.output(asap))


if __name__ == "__main__":
    main()
