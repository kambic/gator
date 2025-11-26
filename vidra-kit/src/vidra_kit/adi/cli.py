import typer
import json
from pathlib import Path
from lxml import etree
from dataclasses import asdict
from .parser import parse_adi, ADIParseError

app = typer.Typer(help="Extracts metadata from ADI.xml files for VOD ingest.")

DEFAULT_SCHEMA = Path(__file__).parent / "schemas" / "CableLabs_ADI.xsd"


@app.command()
def parse(xml_path: Path):
    try:
        metadata = parse_adi(str(xml_path))
        typer.echo(json.dumps(asdict(metadata), indent=2))
    except ADIParseError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def validate(xml_path: Path, schema_path: Path = DEFAULT_SCHEMA):
    try:
        with open(schema_path, "rb") as f:
            schema_doc = etree.XML(f.read())
        schema = etree.XMLSchema(schema_doc)
        doc = etree.parse(str(xml_path))
        schema.assertValid(doc)
        typer.echo("XML is valid.")
    except Exception as e:
        typer.echo(f"Validation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("validate-full")
def run_validate(source_adi: str):
    from .validator_toolkit import validate_stack
    from .validators.adi_validator import adi_provider

    """Trigger full ingest→publish pipeline."""
    result = validate_adi(source_adi)
    typer.echo("[✅] 1/4 Validation complete.")

    result = validate_provider_schema(source_adi)
    typer.echo("[✅] 2/4 Validation complete.")

    result = adi_provider(source_adi)
    typer.echo("[✅] 3/4 Validation complete.")

    result = validate_stack(source_adi)
    typer.echo("[✅] 4/4 Validation complete.")

    typer.echo(f"Workflow started. Root task ID: {result}")


@app.command("validate-kit")
def run_validate_kit(source_adi: str):
    from .validator_toolkit import validate_stack

    """Trigger full ingest→publish pipeline."""
    result = validate_stack(source_adi)
    typer.echo(f"[✅] Validation stack complete. {result}")


def run_cli():

    import argparse
    import yaml

    from vidra_kit.adi.generator import generate_adi_xml_from_dict
    from vidra_kit.adi.validators.adi_validator import adi_provider

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
        adi_provider(args.input)
    else:
        parser.print_help()


if __name__ == "__main__":
    app()
