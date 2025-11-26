# requirements: pip install xsdata[ lxml ] lxml
# from xsdata.formats.dataclass.parsers import XmlParser
# from xsdata.formats.dataclass.parsers.config import ParserConfig
# from xsdata.formats.dataclass.serializers import XmlSerializer
# from xsdata.formats.dataclass.serializers.config import SerializerConfig
# from xsdata.exceptions import ParserError

from lxml import etree
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# ------------------------------------------------------------------
# 1. Auto-generated classes from official ADI XSDs (run once)
# ------------------------------------------------------------------
# Run these commands once to generate Python classes:
#
# xsdata generate adi1.1/ADI.xsd --package adi_models.v1_1
# xsdata generate adi2.0/ADI.xsd --package adi_models.v2_0
#
# This creates perfect Python dataclasses with full validation!

# ------------------------------------------------------------------
# 2. Multi-schema validator (simple to use)
# ------------------------------------------------------------------


class ADIValidator:
    def __init__(self):
        self.schemas = {
            "1.1": Path("schemas/adi1.1/ADI.xsd"),
            "2.0": Path("schemas/adi2.0/ADI.xsd"),
            # Add vendor extensions
            "vendor_xyz": Path("schemas/vendor_xyz_extension.xsd"),
        }
        self.parsers: Dict[str, XmlParser] = {}

    def _load_schema(self, version: str):
        if version not in self.parsers:
            xsd_path = self.schemas.get(version)
            if not xsd_path or not xsd_path.exists():
                raise FileNotFoundError(f"Schema not found: {xsd_path}")

            # Load and cache schema for fast validation
            schema = etree.XMLSchema(etree.parse(str(xsd_path)))
            parser_config = ParserConfig.fail_on_unknown_properties = False
            parser = XmlParser(config=parser_config)
            parser.schema = schema  # attach for validation
            self.parsers[version] = parser
        return self.parsers[version]

    def validate_file(self, xml_path: str | Path, version: str = "auto") -> dict:
        xml_path = Path(xml_path)
        xml_content = xml_path.read_bytes()

        if version == "auto":
            version = self._detect_version(xml_content)

        parser = self._load_schema(version)

        try:
            # This triggers full XSD validation + dataclass parsing
            obj = parser.from_bytes(xml_content)
            return {"valid": True, "version": version, "data": obj, "errors": []}
        except ParserError as e:
            return {
                "valid": False,
                "version": version,
                "data": None,
                "errors": e.messages() if hasattr(e, "messages") else [str(e)],
            }
        except etree.XMLSchemaValidateError as e:
            return {
                "valid": False,
                "version": version,
                "data": None,
                "errors": [str(e)],
            }

    def _detect_version(self, xml_bytes: bytes) -> str:
        """Simple heuristic to detect ADI version"""
        xml_str = xml_bytes.decode("utf-8", errors="ignore")
        if "http://www.cablelabs.com/namespaces/metadata/adi/2.0/" in xml_str:
            return "2.0"
        if "ADI.xsd" in xml_str and "1.1" in xml_str:
            return "1.1"
        return "1.1"  # default fallback


# ------------------------------------------------------------------
# 3. Usage Example
# ------------------------------------------------------------------


def validate_adi(xml_path, xsd_path="schema/ADI.xsd"):
    # Load schema

    print(f"Validating {xml_path} against {xsd_path}...")
    with open(xsd_path, "rb") as f:
        schema_doc = etree.XML(f.read())
    schema = etree.XMLSchema(schema_doc)

    # Parse XML
    xml_doc = etree.parse(xml_path)

    # Validate
    if schema.validate(xml_doc):
        print("ADI.xml is VALID.")
    else:
        print("ADI.xml is INVALID.")
        for error in schema.error_log:
            print(f"- Line {error.line}, Col {error.column}: {error.message}")


from pathlib import Path

schemas = Path("schemas")

adi = "/home/e-kambicr/neo/alligator/vidra-kit/src/vidra_kit/adi/sample_adi.xml"

for schema in schemas.glob("*.xsd"):
    validate_adi(adi, str(schema.absolute()))

print("done")


if __name__ == "__main__":
    validator = ADIValidator()

    result = validator.validate_file("examples/batman_movie.xml", version="auto")

    if result["valid"]:
        print(f"ADI XML is VALID (version {result['version']})")
        # Access parsed data cleanly
        title = result["data"].Metadata.App_Data[0].Value
        print(f"Title: {title}")
    else:
        print(f"INVALID XML (detected version: {result['version']})")
        for err in result["errors"]:
            print(f"   - {err}")
