from lxml import etree


def validate_adi(xml_path):
    print(f"[INFO] Validating ADI XML: {xml_path}")
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
        if root.tag != "ADI":
            print("[ERROR] Root tag is not <ADI>")
        else:
            print("[✓] Root tag is valid")
        # Add more validation logic as needed
    except Exception as e:
        print(f"[ERROR] Failed to parse XML: {e}")


##########################################################################################
import os
import sys
from lxml import etree

# === CONFIG ===
ADI_XSD_PATH = "ADI.xsd"  # Replace with your actual schema file path (optional)
REQUIRED_TAGS = ["Metadata", "AMS", "App_Data", "Asset"]


def load_xml(xml_path):
    try:
        with open(xml_path, "rb") as f:
            return etree.parse(f)
    except etree.XMLSyntaxError as e:
        print(f"[ERROR] XML syntax error: {e}")
        sys.exit(1)


def validate_against_schema(xml_tree, xsd_path):
    if not os.path.exists(xsd_path):
        print(
            f"[WARNING] No XSD schema found at {xsd_path}. Skipping schema validation."
        )
        return

    with open(xsd_path, "rb") as f:
        schema_doc = etree.parse(f)
        schema = etree.XMLSchema(schema_doc)

    if not schema.validate(xml_tree):
        print("[ERROR] Schema validation failed.")
        for e in schema.error_log:
            print(f" - Line {e.line}: {e.message}")
        sys.exit(1)
    else:
        print("[OK] Schema validation passed.")


def check_required_tags(xml_tree):
    root = xml_tree.getroot()
    missing_tags = []

    for tag in REQUIRED_TAGS:
        if not root.xpath(f".//{tag}"):
            missing_tags.append(tag)

    if missing_tags:
        print(f"[ERROR] Missing required tags: {', '.join(missing_tags)}")
        sys.exit(1)
    else:
        print("[OK] All required tags are present.")


def validate_asset_consistency(xml_tree):
    assets = xml_tree.xpath("//Asset")
    asset_ids = set()

    for asset in assets:
        asset_id = asset.xpath(".//AMS/@Asset_ID")
        if asset_id:
            asset_ids.add(asset_id[0])

    if not asset_ids:
        print("[ERROR] No Asset_IDs found.")
        sys.exit(1)

    print(f"[OK] Found {len(asset_ids)} unique Asset_ID(s).")


def main(xml_file):
    print(f"Validating ADI file: {xml_file}")
    xml_tree = load_xml(xml_file)
    validate_against_schema(xml_tree, ADI_XSD_PATH)
    check_required_tags(xml_tree)
    validate_asset_consistency(xml_tree)
    print("[✅] Validation completed successfully.")


def validate_provider_schema(xml_file):
    main(xml_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python adi_validator.py <path_to_ADI.xml>")
        sys.exit(1)

    main(sys.argv[1])
