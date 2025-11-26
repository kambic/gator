```
from adi_parser import parse_adi

adi = parse_adi("input/ADI.xml")

print(adi.metadata["Provider"])
for asset in adi.assets:
    print(asset.metadata.get("Content_Type"), asset.metadata.get("Title"))

```

# Print parsed ADI metadata

`adi-parser parse input/ADI.xml`

# Dump parsed metadata to JSON

`adi-parser dump input/ADI.xml -o output.json`

Usage Examples
Parse and Pretty Print:

`adi-parser parse input/ADI.xml --pretty`

Dump to JSON:

`adi-parser dump input/ADI.xml -o out.json`

Validate Against Schema:

`adi-parser validate input/ADI.xml --schema CableLabs_ADI.xsd`

```
from setuptools import setup, find_packages

setup( # ...
include_package_data=True,
package_data={
"adi_parser": ["schemas/*.xsd"],
},
)
```

📦 Update setup.py to include .xsd files in the package

Add this to ensure the XSDs are packaged:

```
from setuptools import setup, find_packages

setup( # ...
include_package_data=True,
package_data={
"adi_parser": ["schemas/*.xsd"],
},
)
```

Also add a MANIFEST.in in the root of your project:

`recursive-include adi_parser/schemas \*.xsd`

✅ Usage Examples
Validate with schema profile:

`adi-parser validate input/ADI.xml --profile cablelabs`

Validate with explicit .xsd path:

`adi-parser validate input/ADI.xml --schema /path/to/custom.xsd`
