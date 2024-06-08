# ASAP PMP Report Parser

A Python CLI tool for parsing and validating ASAP reports.

The ASAP standard is a flat file developed by the 
American Society For Automation in Pharmacy.  https://asapnet.org/

The ASAP format is delimited flat file format that uses `~` as section delimiters and `*` as field delimiters.

## Setup

```shell
pipenv install
pipenv run python -m app --help
```

## Parsing ASAP files

```shell
pipenv run python -m app path/to/asap.txt
```

### Command line options

`-u` or `--unsafe-phi-display` - Display PHI data in the output. By default, PHI data is redacted.

`--help` - Display help message.

---  
## Eventual Steps for Distributing on PyPi

The setup.py file includes some advanced patterns and best 
practices for setup.py, as well as some commented–out nice–to–haves. For example, it provides a `python 
setup.py upload` command, which creates a universal wheel (and sdist) and uploads your package to PyPi using Twine. 
It also creates/uploads a new git tag, automatically.

### Packaging 

Update `setup.py` with your details and then run `python setup.py upload` to package for distribution on PyPi.

