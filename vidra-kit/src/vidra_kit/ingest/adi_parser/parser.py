from lxml import etree
from .models import ADIMetadata, Asset, AppData
from .exceptions import ADIParseError
from .utils import get_text


def parse_adi(xml_path: str) -> ADIMetadata:
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()

        if root.tag != "ADI":
            raise ADIParseError("Root tag is not ADI")

        metadata_elem = root.find("Metadata")
        if metadata_elem is None:
            raise ADIParseError("Missing Metadata element")

        # Extract global metadata
        global_metadata = {
            md.get("Name"): md.text
            for md in metadata_elem.findall("App_Data")
            if md.get("Name")
        }

        # Parse assets
        assets = []
        for asset_elem in root.findall("Asset"):
            asset_metadata = {}
            app_data_items = []

            asset_metadata_elem = asset_elem.find("Metadata")
            if asset_metadata_elem is not None:
                for data in asset_metadata_elem.findall("App_Data"):
                    name = data.get("Name")
                    value = data.get("Value", data.text)
                    if name:
                        asset_metadata[name] = value
                        app_data_items.append(AppData(name=name, value=value))

            assets.append(Asset(metadata=asset_metadata, app_data=app_data_items))

        return ADIMetadata(metadata=global_metadata, assets=assets)

    except etree.XMLSyntaxError as e:
        raise ADIParseError(f"Invalid XML: {str(e)}")
    except Exception as e:
        raise ADIParseError(f"Unexpected error: {str(e)}")
