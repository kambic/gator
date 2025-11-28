from lxml import etree
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# --- Data Model (No Change Needed, Already Modern) ---


class ADIParseError(Exception):
    """Raised when ADI parsing fails due to structural or validation issues."""

    pass


@dataclass
class AppData:
    """Represents a single Name/Value pair within ADI's App_Data."""

    name: str
    value: str


@dataclass
class Asset:
    """Represents an Asset block containing metadata and optional AppData."""

    metadata: Dict[str, str]
    # AppData is now the primary source of truth, metadata is derived/convenience
    app_data: List[AppData] = field(default_factory=list)


@dataclass
class ADIMetadata:
    """Represents the root ADI document structure."""

    metadata: Dict[str, str]
    assets: List[Asset] = field(default_factory=list)


# --- Class-Based Parser (Refactored Logic) ---


class ADIParser:
    """
    A class to parse an ADI (Asset Distribution Interface) XML file
    into a structured ADIMetadata object.
    """

    # XML Namespace used in typical VOD ADI files (optional, but good practice)
    # If the ADI uses namespaces, you'd need to uncomment and use this
    # NSMAP = {'adi': 'http://www.scte.org/schemas/1.0/adi'}

    def __init__(self, xml_path: str):
        """Initializes the parser with the path to the ADI XML file."""
        self.xml_path = xml_path
        self._root: Optional[etree._Element] = None

    def _load_and_validate_root(self) -> etree._Element:
        """Loads the XML tree and validates the root tag."""
        try:
            tree = etree.parse(self.xml_path)
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            raise ADIParseError(f"Invalid XML syntax in '{self.xml_path}': {str(e)}")

        # Check the root tag, ignoring potential namespace prefix
        if etree.QName(root).localname != "ADI":
            raise ADIParseError(
                f"Root tag is not 'ADI', found '{etree.QName(root).localname}'"
            )

        return root

    def _parse_app_data_elements(self, element: etree._Element) -> List[AppData]:
        """
        Extracts App_Data elements from a parent element (Metadata or Asset).

        In ADI 1.1/2.0, App_Data is often structured like:
        <App_Data Name="Name" Value="Value"/> OR <App_Data Name="Name">Value</App_Data>
        """
        app_data_list = []
        for data_elem in element.findall("App_Data"):
            name = data_elem.get("Name")
            # Prefer 'Value' attribute, fall back to element text
            value = data_elem.get("Value", data_elem.text)

            if name and value is not None:
                app_data_list.append(AppData(name=name, value=value))

        return app_data_list

    def _app_data_list_to_dict(self, app_data_list: List[AppData]) -> Dict[str, str]:
        """Converts a list of AppData objects into a simple Name:Value dictionary."""
        return {item.name: item.value for item in app_data_list}

    def _parse_metadata(self, root_element: etree._Element) -> Dict[str, str]:
        """Extracts the global ADI Metadata."""
        metadata_elem = root_element.find("Metadata")
        if metadata_elem is None:
            raise ADIParseError("Missing 'Metadata' element in ADI root.")

        app_data_list = self._parse_app_data_elements(metadata_elem)
        return self._app_data_list_to_dict(app_data_list)

    def _parse_assets(self, root_element: etree._Element) -> List[Asset]:
        """Extracts all Asset blocks from the ADI document."""
        assets = []
        for asset_elem in root_element.findall("Asset"):
            asset_metadata_elem = asset_elem.find("Metadata")

            if asset_metadata_elem is not None:
                # Get the App_Data list for this asset
                asset_app_data = self._parse_app_data_elements(asset_metadata_elem)
                # Convert the list to a dictionary for easy access
                asset_metadata_dict = self._app_data_list_to_dict(asset_app_data)

                assets.append(
                    Asset(metadata=asset_metadata_dict, app_data=asset_app_data)
                )
            # An Asset block without a Metadata block is technically possible but often invalid

        return assets

    def parse(self) -> ADIMetadata:
        """The main method to execute the parsing process."""
        try:
            root = self._load_and_validate_root()

            global_metadata = self._parse_metadata(root)
            assets = self._parse_assets(root)

            return ADIMetadata(metadata=global_metadata, assets=assets)

        except ADIParseError:
            # Re-raise known structural errors
            raise
        except Exception as e:
            # Catch all other unexpected errors (e.g., file not found)
            raise ADIParseError(f"Unexpected error during parsing: {str(e)}")


# --- Example Usage ---
