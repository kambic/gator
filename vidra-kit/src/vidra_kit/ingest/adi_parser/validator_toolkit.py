import json
import sys
from datetime import datetime

from lxml import etree
import logging

import yaml

logger = logging.getLogger(__name__)

# === EMBEDDED XSD (combined movie/poster support) ===
ADI_XSD_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           elementFormDefault="qualified">

  <xs:element name="ADI">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="Metadata" type="MetadataType"/>
        <xs:element name="Asset" type="AssetType" maxOccurs="unbounded"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

  <xs:complexType name="MetadataType">
    <xs:sequence>
      <xs:element name="AMS" type="AMSType"/>
      <xs:element name="App_Data" type="AppDataType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <xs:complexType name="AssetType">
    <xs:sequence>
      <xs:element name="Metadata" type="MetadataType"/>
    </xs:sequence>
  </xs:complexType>

  <xs:complexType name="AMSType">
    <xs:attribute name="Asset_ID" type="xs:string" use="required"/>
    <xs:attribute name="Asset_Class" type="xs:string" use="required"/>
    <xs:attribute name="Asset_Name" type="xs:string"/>
    <xs:attribute name="Version_Major" type="xs:string"/>
    <xs:attribute name="Version_Minor" type="xs:string"/>
    <xs:attribute name="Description" type="xs:string"/>
    <xs:attribute name="Creation_Date" type="xs:dateTime"/>
  </xs:complexType>

  <xs:complexType name="AppDataType">
    <xs:attribute name="App" type="xs:string" use="required"/>
    <xs:attribute name="Name" type="xs:string" use="required"/>
    <xs:attribute name="Value" type="xs:string" use="required"/>
  </xs:complexType>

</xs:schema>
"""

ADI_XSD_PATH = "ADI.xsd"  # Replace with your actual schema file path (optional)
REQUIRED_TAGS = ["Metadata", "AMS", "App_Data", "Asset"]


def load_xml(xml_path):
    try:
        with open(xml_path, "rb") as f:
            return etree.parse(f)
    except etree.XMLSyntaxError as e:
        logger.info(f"[ERROR] XML syntax error: {e}")
        sys.exit(1)


def validate_against_embedded_schema(xml_tree):
    xsd_doc = etree.XML(ADI_XSD_CONTENT.encode("utf-8"))
    schema = etree.XMLSchema(xsd_doc)
    if not schema.validate(xml_tree):
        logger.info("[ERROR] Schema validation failed.")
        for e in schema.error_log:
            logger.info(f" - Line {e.line}: {e.message}")
        sys.exit(1)
    logger.info("[OK] Schema validation passed.")


def check_required_tags(xml_tree):
    root = xml_tree.getroot()
    for tag in ["Metadata", "Asset"]:
        if not root.xpath(f".//{tag}"):
            logger.info(f"[ERROR] Missing required tag: {tag}")
            sys.exit(1)
    logger.info("[OK] Required tags present.")


def autofix(xml_tree):
    logger.info("🔧 Attempting auto-fix of minor issues...")

    for ams in xml_tree.xpath("//AMS"):
        if not ams.get("Creation_Date"):
            now = datetime.utcnow().isoformat() + "Z"
            ams.set("Creation_Date", now)
            logger.info(f" - Added missing Creation_Date: {now}")

        if not ams.get("Version_Major"):
            ams.set("Version_Major", "1")
            logger.info(" - Added default Version_Major: 1")

        if not ams.get("Version_Minor"):
            ams.set("Version_Minor", "0")
            logger.info(" - Added default Version_Minor: 0")

        cls = ams.get("Asset_Class")
        if cls and cls != cls.lower():
            ams.set("Asset_Class", cls.lower())
            logger.info(f" - Normalized Asset_Class: {cls.lower()}")

    return xml_tree


def validate_asset_consistency(xml_tree):
    asset_ids = {
        a.get("Asset_ID") for a in xml_tree.xpath("//AMS") if a.get("Asset_ID")
    }
    logger.info(f"[OK] Found {len(asset_ids)} unique Asset_ID(s).")


def write_fixed_xml(xml_tree, out_path):
    with open(out_path, "wb") as f:
        f.write(
            etree.tostring(
                xml_tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"
            )
        )
    logger.info(f"[💾] Fixed ADI XML written to: {out_path}")


def generate_adi_xml(title, asset_id, poster_id, output_path):
    now = datetime.utcnow().isoformat() + "Z"

    adi = etree.Element("ADI")

    metadata = etree.SubElement(adi, "Metadata")
    etree.SubElement(
        metadata, "AMS", Asset_ID=asset_id, Asset_Class="title", Creation_Date=now
    )
    etree.SubElement(metadata, "App_Data", App="MOD", Name="Title", Value=title)

    def add_asset(aid, aclass, app_data):
        asset = etree.SubElement(adi, "Asset")
        meta = etree.SubElement(asset, "Metadata")
        etree.SubElement(
            meta, "AMS", Asset_ID=aid, Asset_Class=aclass, Creation_Date=now
        )
        for k, v in app_data.items():
            etree.SubElement(meta, "App_Data", App="MOD", Name=k, Value=v)

    add_asset(asset_id + "-VID", "movie", {"Type": "video"})
    add_asset(poster_id, "poster", {"Resolution": "1920x1080"})

    tree = etree.ElementTree(adi)
    with open(output_path, "wb") as f:
        f.write(
            etree.tostring(
                tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"
            )
        )

    logger.info(f"[✅] ADI XML generated at {output_path}")


def generate_adi_xml_from_dict(data, output_path):
    now = datetime.utcnow().isoformat() + "Z"

    title = data.get("title", "Untitled")
    asset_id = data.get("asset_id", "MOV0000")
    poster_id = data.get("poster_id", "POST0000")
    resolution = data.get("poster_resolution", "1920x1080")
    bitrate = data.get("movie_bitrate", "8000000")

    adi = etree.Element("ADI")

    # Root Metadata
    metadata = etree.SubElement(adi, "Metadata")
    etree.SubElement(
        metadata, "AMS", Asset_ID=asset_id, Asset_Class="title", Creation_Date=now
    )
    etree.SubElement(metadata, "App_Data", App="MOD", Name="Title", Value=title)

    def add_asset(aid, aclass, app_data):
        asset = etree.SubElement(adi, "Asset")
        meta = etree.SubElement(asset, "Metadata")
        etree.SubElement(
            meta, "AMS", Asset_ID=aid, Asset_Class=aclass, Creation_Date=now
        )
        for k, v in app_data.items():
            etree.SubElement(meta, "App_Data", App="MOD", Name=k, Value=v)

    add_asset(asset_id + "-VID", "movie", {"Type": "video", "Bitrate": bitrate})

    add_asset(poster_id, "poster", {"Resolution": resolution})

    tree = etree.ElementTree(adi)
    with open(output_path, "wb") as f:
        f.write(
            etree.tostring(
                tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"
            )
        )
    logger.info(f"[✅] ADI XML generated at {output_path}")


def validate_stack(xml_file):
    tree = load_xml(xml_file)
    autofix(tree)
    validate_against_embedded_schema(tree)
    check_required_tags(tree)
    validate_asset_consistency(tree)
    write_fixed_xml(tree, "fixed_" + xml_file)
    logger.info("[✅] Validation complete.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Validate: python adi_toolkit.py validate input.xml")
        print(
            "  Generate: python adi_toolkit.py generate '<title>' <movie_id> <poster_id> <output.xml>"
        )
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "validate":
        xml_file = sys.argv[2]
        validate_stack(xml_file)

    elif command == "generate":
        if len(sys.argv) != 6:
            print(
                "Usage: python adi_toolkit.py generate '<title>' <movie_id> <poster_id> <output.xml>"
            )
            sys.exit(1)
        title, movie_id, poster_id, out_path = sys.argv[2:6]
        generate_adi_xml(title, movie_id, poster_id, out_path)

    elif command == "generatefile":
        if len(sys.argv) != 4:
            print(
                "Usage: python adi_toolkit.py generatefile <input.yaml|json> <output.xml>"
            )
            sys.exit(1)

        input_file = sys.argv[2]
        output_file = sys.argv[3]

        if input_file.endswith(".yaml") or input_file.endswith(".yml"):
            with open(input_file, "r") as f:
                data = yaml.safe_load(f)
        elif input_file.endswith(".json"):
            with open(input_file, "r") as f:
                data = json.load(f)
        else:
            print("[ERROR] Unsupported input format. Use .yaml or .json.")
            sys.exit(1)

        generate_adi_xml_from_dict(data, output_file)

    else:
        print("[ERROR] Unknown command. Use 'validate' or 'generate'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
