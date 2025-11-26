import sys
import tempfile
from lxml import etree

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


def load_xml(xml_path):
    try:
        with open(xml_path, "rb") as f:
            return etree.parse(f)
    except etree.XMLSyntaxError as e:
        print(f"[ERROR] XML syntax error: {e}")
        sys.exit(1)


def validate_against_embedded_schema(xml_tree):
    try:
        xsd_doc = etree.XML(ADI_XSD_CONTENT.encode("utf-8"))
        schema = etree.XMLSchema(xsd_doc)

        if not schema.validate(xml_tree):
            print("[ERROR] Schema validation failed.")
            for e in schema.error_log:
                print(f" - Line {e.line}: {e.message}")
            sys.exit(1)
        else:
            print("[OK] Schema validation passed.")
    except Exception as e:
        print(f"[ERROR] Schema processing failed: {e}")
        sys.exit(1)


def check_required_tags(xml_tree):
    root = xml_tree.getroot()
    missing = []
    for tag in ["Metadata", "Asset"]:
        if not root.xpath(f".//{tag}"):
            missing.append(tag)

    if missing:
        print(f"[ERROR] Missing required top-level elements: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("[OK] Required XML structure is intact.")


def validate_asset_consistency(xml_tree):
    asset_elements = xml_tree.xpath("//Asset")
    asset_ids = set()
    posters = 0
    movies = 0

    for asset in asset_elements:
        asset_id = asset.xpath(".//AMS/@Asset_ID")
        asset_class = asset.xpath(".//AMS/@Asset_Class")
        if asset_id:
            asset_ids.add(asset_id[0])
        if asset_class:
            if asset_class[0] == "poster":
                posters += 1
            elif asset_class[0] == "movie":
                movies += 1

    if not asset_ids:
        print("[ERROR] No Asset_IDs found.")
        sys.exit(1)

    print(
        f"[OK] Found {len(asset_ids)} unique assets. {movies} movie(s), {posters} poster(s)."
    )


def adi_provider(xml_file):

    print(f"🔍 Validating ADI file: {xml_file}")
    xml_tree = load_xml(xml_file)
    validate_against_embedded_schema(xml_tree)
    check_required_tags(xml_tree)
    validate_asset_consistency(xml_tree)
    print("[✅] Validation completed successfully.")


def main(xml_file):
    adi_provider(xml_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python adi_validator.py <path_to_ADI.xml>")
        sys.exit(1)

    main(sys.argv[1])
