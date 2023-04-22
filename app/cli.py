from argparse import ArgumentParser

from app.asap import (
    ASAP,
    InvalidASAPFile,
)
from app.output_formats import ASAPHTMLOutput


def main():
    parser = ArgumentParser(prog="cli")
    parser.add_argument("filepath", help="ASAP filepath")
    args = parser.parse_args()
    print("Opening: " + args.filepath)

    try:
        with open(args.filepath, "r") as my_file:
            asap = ASAP(my_file.read())
    except InvalidASAPFile:
        print(
            f"File {args.filepath} is not an ASAP file.  File must be text and begin with an ASAP header."
        )

    # Print basic stats
    asap.analyze()

    # Output HTML format
    html = ASAPHTMLOutput()
    print("Outputting ")
    with open("asap_report.html", "w") as text_file:
        text_file.write(html.output(asap))


if __name__ == "__main__":
    main()
