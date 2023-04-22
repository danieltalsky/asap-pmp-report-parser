from argparse import ArgumentParser

from app.asap import (
    ASAP,
    InvalidASAPFile,
)

def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument('filepath', help="ASAP filepath")
    args = parser.parse_args()
    print("Opening: " + args.filepath)


    try:
        with open(args.filepath, 'r') as my_file:
            asap = ASAP(my_file.read())
            asap.analyze()
    except InvalidASAPFile:
        print(f'File {args.filepath} is not an ASAP file.  File must be text and begin with an ASAP header.')


if __name__ == '__main__':
    main()
