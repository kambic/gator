import argparse
import json
import sys
from dataclasses import asdict
from lxml import etree
from .parser import parse_adi
from .exceptions import ADIParseError
from colorama import init, Fore, Style

init(autoreset=True)


def pretty_print(data, indent=0):
    for key, value in data.items():
        if isinstance(value, dict):
            print(" " * indent + f"{Fore.YELLOW}{key}:{Style.RESET_ALL}")
            pretty_print(value, indent + 2)
        elif isinstance(value, list):
            print(" " * indent + f"{Fore.YELLOW}{key}:{Style.RESET_ALL}")
            for item in value:
                if isinstance(item, dict):
                    pretty_print(item, indent + 2)
                else:
                    print(" " * (indent + 2) + str(item))
        else:
            print(" " * indent + f"{Fore.CYAN}{key}: {Style.RESET_ALL}{value}")


import os
from pathlib import Path

DEFAULT_SCHEMA_DIR = Path(__file__).parent / "schemas"
DEFAULT_PROFILE = "cablelabs"

PROFILE_SCHEMA_MAP = {
    "cablelabs": "CableLabs_ADI.xsd",
    "provider_xyz": "ProviderXYZ_ADI.xsd",
}


def validate_xml(xml_path, schema_path=None, profile=None):
    try:
        if not schema_path:
            profile = profile or DEFAULT_PROFILE
            schema_file = PROFILE_SCHEMA_MAP.get(profile.lower())

            if not schema_file:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Unknown profile: {profile}")
                sys.exit(1)

            schema_path = DEFAULT_SCHEMA_DIR / schema_file
            if not schema_path.exists():
                print(
                    f"{Fore.RED}[ERROR]{Style.RESET_ALL} Schema file not found: {schema_path}"
                )
                sys.exit(1)

        with open(schema_path, "rb") as f:
            schema_doc = etree.XML(f.read())
        schema = etree.XMLSchema(schema_doc)

        doc = etree.parse(xml_path)
        schema.assertValid(doc)
        print(
            f"{Fore.GREEN}[VALID]{Style.RESET_ALL} XML is valid against schema: {schema_path.name}"
        )
    except (etree.XMLSchemaError, etree.DocumentInvalid) as e:
        print(f"{Fore.RED}[INVALID]{Style.RESET_ALL} {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Schema validation failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ADI Parser CLI - Extract metadata from ADI XML files."
    )
    parser.add_argument(
        "command", choices=["parse", "dump", "validate"], help="Command to run"
    )
    parser.add_argument("xml_path", help="Path to the ADI XML file")
    parser.add_argument("-o", "--output", help="Output JSON path (for dump)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print metadata")
    parser.add_argument("--schema", help="Path to XML Schema (.xsd) for validation")
    parser.add_argument(
        "--profile", help="Schema profile to use (e.g. cablelabs, provider_xyz)"
    )

    args = parser.parse_args()

    if args.command == "validate":
        if not args.schema:
            print(f"{Fore.RED}--schema is required for validation{Style.RESET_ALL}")
            sys.exit(1)
        # validate_xml(args.xml_path, args.schema)
        validate_xml(args.xml_path, schema_path=args.schema, profile=args.profile)
        return

    try:
        metadata = parse_adi(args.xml_path)
        metadata_dict = asdict(metadata)

        if args.command == "parse":
            if args.pretty:
                pretty_print(metadata_dict)
            else:
                print(json.dumps(metadata_dict, indent=2))

        elif args.command == "dump":
            if not args.output:
                print("Error: --output is required for 'dump' command", file=sys.stderr)
                sys.exit(1)
            with open(args.output, "w") as f:
                json.dump(metadata_dict, f, indent=2)
            print(f"Metadata dumped to {args.output}")

    except ADIParseError as e:
        print(f"[ERROR] Failed to parse ADI file: {e}", file=sys.stderr)
        sys.exit(1)


def adi_toolkit():
    main()
