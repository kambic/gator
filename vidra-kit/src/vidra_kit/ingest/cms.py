import json

import requests

cookie = "Cookie: lb_mtcms=ffffffff09722b5745525d5f4f58455e445a4a423660"

headers = {
    "Authorization": "MTCMS_API_TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0c2RhNTY3ODkwIiwibmFtZSI6IkpvaGRzYXNhZG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.KRj7Nv_a2Q4O4029fYXmn_oLQYwBRFaa3CyJ28ZORGk",
}


def get_ids():
    url = "https://mtcms.telekom.si/api/output/vodOfferIds?catalogueId={{catalog_id}}&catalogueCategoryId={{catalog_category_id}}"
    res = requests.get(url, headers=headers, verify=False)

    data = res.json()

    with open("ids.txt", "w") as f:
        for val in data:
            f.write(f"{val}\n")


import re


def extract_all_urls(data):
    urls = []
    url_pattern = re.compile(r'rtsp?://[^\s",>]+')

    def recurse(item):
        if isinstance(item, dict):
            for v in item.values():
                recurse(v)
        elif isinstance(item, list):
            for v in item:
                recurse(v)
        elif isinstance(item, str):
            if url_pattern.match(item):
                urls.append(item)

    recurse(data)
    return urls


def extract_url_keys(data):
    urls = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() == "url" and isinstance(value, str):
                urls.append(value)
            else:
                urls.extend(extract_url_keys(value))
    elif isinstance(data, list):
        for item in data:
            urls.extend(extract_url_keys(item))

    return urls


def get_catalogue():
    url = "https://mtcms.telekom.si/api/output/catalogue/items?id=e5df836694107c7932b26b84"
    res = requests.get(url, headers=headers, verify=False)

    data = res.json()
    c = data["catalogue"]

    with open("catalogue.json", "w") as f:
        f.write(json.dumps(c, indent=4))



def extractor():
    # Load JSON from a file
    with open("catalogue.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data = extract_all_urls(data)

    with open("videoURL.txt", "w") as f:
        for d in data:
            f.write(d)
            f.write("\n")
        # f.write(json.dumps(data, indent=4))


extractor()
