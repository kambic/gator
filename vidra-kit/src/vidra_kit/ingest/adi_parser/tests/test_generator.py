import tempfile

import yaml
from adi_toolkit.generator import generate_adi_xml_from_dict
from lxml import etree


def test_generate_minimal_adi():
    sample = {
        "title": {"en": "Test Movie"},
        "asset_id": "TEST123",
        "poster_id": "TEST123-POSTER",
        "poster_resolution": "1920x1080",
        "movie_bitrate": "8000000",
        "default_lang": "en",
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp:
        generate_adi_xml_from_dict(sample, temp.name)
        tree = etree.parse(temp.name)
        assert tree.getroot().tag == "ADI"
        assert tree.xpath("//AMS[@Asset_Class='title']")[0].get("Asset_ID") == "TEST123"
