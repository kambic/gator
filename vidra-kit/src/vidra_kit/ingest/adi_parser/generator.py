from datetime import datetime

from lxml import etree

VALID_LANGS = {"en", "fr", "es", "de", "it", "pt"}


def add_localized_app_data(parent, name, content, default_lang=None):
    if isinstance(content, dict):
        for lang, val in content.items():
            if lang not in VALID_LANGS:
                print(f"[WARN] Skipping unsupported lang code '{lang}'.")
                continue
            etree.SubElement(
                parent, "App_Data", App="MOD", Name=name, Value=val, Lang=lang
            )
        if default_lang and default_lang in content:
            fallback_val = content[default_lang]
            for lang in VALID_LANGS - set(content.keys()):
                etree.SubElement(
                    parent,
                    "App_Data",
                    App="MOD",
                    Name=name,
                    Value=fallback_val,
                    Lang=lang,
                )
    elif content:
        etree.SubElement(parent, "App_Data", App="MOD", Name=name, Value=str(content))


def generate_adi_xml_from_dict(data, output_path):
    now = datetime.utcnow().isoformat() + "Z"
    root = etree.Element("ADI")
    metadata = etree.SubElement(root, "Metadata")
    etree.SubElement(
        metadata,
        "AMS",
        Asset_ID=data["asset_id"],
        Asset_Class="title",
        Creation_Date=now,
    )

    for field in ["title", "synopsis", "genre", "actors", "director", "studio"]:
        if field in data:
            add_localized_app_data(
                metadata,
                field.capitalize(),
                data[field],
                default_lang=data.get("default_lang"),
            )

    def add_asset(asset_id, asset_class, app_data):
        asset = etree.SubElement(root, "Asset")
        meta = etree.SubElement(asset, "Metadata")
        etree.SubElement(
            meta, "AMS", Asset_ID=asset_id, Asset_Class=asset_class, Creation_Date=now
        )
        for k, v in app_data.items():
            if isinstance(v, dict):
                add_localized_app_data(
                    meta, k, v, default_lang=data.get("default_lang")
                )
            else:
                etree.SubElement(meta, "App_Data", App="MOD", Name=k, Value=str(v))

    add_asset(
        f"{data['asset_id']}-VID",
        "movie",
        {"Type": "video", "Bitrate": data.get("movie_bitrate")},
    )
    add_asset(
        data["poster_id"], "poster", {"Resolution": data.get("poster_resolution")}
    )
    if "trailer_id" in data:
        add_asset(
            data["trailer_id"],
            "trailer",
            {"Type": "video", "Bitrate": data.get("trailer_bitrate")},
        )

    tree = etree.ElementTree(root)
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"[✓] ADI XML generated: {output_path}")
