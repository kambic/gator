import argparse
import json

import yaml

from vidra_kit.adi.generator import generate_adi_xml_from_dict
from vidra_kit.adi.validator import validate_adi


def run_cli():
    parser = argparse.ArgumentParser(
        prog="adi-toolkit", description="ADI XML Generator and Validator"
    )
    subparsers = parser.add_subparsers(dest="command")

    g = subparsers.add_parser("generate", help="Generate ADI XML from metadata")
    g.add_argument("input", help="Input YAML or JSON file")
    g.add_argument("output", help="Output ADI XML file")

    v = subparsers.add_parser("validate", help="Validate ADI XML")
    v.add_argument("input", help="ADI XML to validate")

    args = parser.parse_args()

    if args.command == "generate":
        with open(args.input, "r") as f:
            if args.input.endswith((".yaml", ".yml")):
                metadata = yaml.safe_load(f)
            elif args.input.endswith(".json"):
                metadata = json.load(f)
            else:
                print("[ERROR] Input must be a YAML or JSON file")
                return
        generate_adi_xml_from_dict(metadata, args.output)

    elif args.command == "validate":
        validate_adi(args.input)
    else:
        parser.print_help()


if __name__ == "__main__":
    run_cli()
