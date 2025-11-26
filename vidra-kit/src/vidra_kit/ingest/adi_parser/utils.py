def get_text(element, tag_name):
    tag = element.find(tag_name)
    return tag.text.strip() if tag is not None and tag.text else ""
