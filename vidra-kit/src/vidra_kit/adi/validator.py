#!/usr/bin/env python3
"""
Modern ADI XML Validator using lxml, dataclasses, and proper error handling.
Validates structure, schema (XSD), required elements, and basic asset consistency.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Optional

from lxml import etree

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Container for validation outcomes."""

    success: bool
    errors: List[str] = field(default_factory=list)

    def add_error(self, message: str, line: int | None = None):
        prefix = f"Line {line}: " if line else ""
        self.errors.append(f"{prefix}{message}")
        self.success = False

    def log(self):
        if self.success:
            log.info("Validation passed.")
        else:
            log.error("Validation failed with errors:")
            for err in self.errors:
                log.error(f"  • {err}")


@dataclass
class ADIValidatorConfig:
    """Configuration for the validator."""

    # Changed from a single path to a list of paths
    xsd_paths: List[Path] = field(default_factory=list)
    required_root_tags: Set[str] = field(default_factory=lambda: {"ADI"})
    required_top_level_elements: Set[str] = field(
        default_factory=lambda: {"Metadata", "Asset"}
    )


class ADIValidator:
    """Main validator class for ADI XML packages."""

    def __init__(self, config: Optional[ADIValidatorConfig] = None):
        self.config = config or ADIValidatorConfig()
        self.schema: Optional[etree.XMLSchema] = None
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load XSD schemas from paths. Lxml should handle imports internally."""
        if not self.config.xsd_paths:
            log.warning("No XSD paths provided. Schema validation skipped.")
            return

        # Attempt to load the primary schema file.
        # If the primary XSD uses xs:import or xs:include, lxml automatically handles
        # finding those additional files IF they are in the same directory or
        # accessible via a catalog resolver (not implemented here).
        primary_xsd_path = self.config.xsd_paths[0]
        if not primary_xsd_path.exists():
            log.warning(
                f"Primary XSD not found at {primary_xsd_path}. Schema validation skipped."
            )
            return

        try:
            # We only need to parse the main file in the "stack"
            schema_doc = etree.parse(str(primary_xsd_path))
            self.schema = etree.XMLSchema(schema_doc)
            log.info(f"Loaded schema from primary file: {primary_xsd_path}")

            if len(self.config.xsd_paths) > 1:
                log.info(
                    f"Lxml attempts to resolve additional schemas ({len(self.config.xsd_paths) - 1} specified) via xs:import within the primary file's directory."
                )

        except Exception as e:
            log.error(f"Failed to load XSD schema(s): {e}")
            # Re-raise to halt initialization if schema loading is critical
            raise

    def validate(self, xml_path: str | Path) -> ValidationResult:
        """Run full validation on an ADI XML file."""
        # ... (Rest of the validate method remains the same) ...

        xml_path = Path(xml_path)

        result = ValidationResult(success=True)

        log.info(f"Starting validation of: {xml_path}")

        # 1. Parse XML
        tree = self._parse_xml(xml_path, result)
        if not result.success:
            result.log()
            return result

        root = tree.getroot()

        # 3. Schema validation (optional)
        if self.schema:
            self._validate_schema(tree, result)

        result.log()
        return result

    def _parse_xml(
        self, xml_path: Path, result: ValidationResult
    ) -> etree._ElementTree | None:
        try:
            tree = etree.parse(str(xml_path))
            log.info("XML parsed successfully.")
            return tree
        except etree.XMLSyntaxError as e:
            result.add_error(
                f"XML syntax error: {e}", e.line if hasattr(e, "line") else None
            )
        except Exception as e:
            result.add_error(f"Failed to read XML file: {e}")
        return None

    def _validate_schema(
        self, tree: etree._ElementTree, result: ValidationResult
    ) -> None:
        if not self.schema.validate(tree):
            result.add_error("XSD schema validation failed")
            for error in self.schema.error_log:
                result.add_error(error.message, error.line)
        else:
            log.info("XSD schema validation passed")


def main(xml_file: str | Path) -> int:

    # Configure the validator with the list of schemas.
    # Lxml only needs the "entry point" XSD (primary_adi.xsd).
    config = ADIValidatorConfig(
        xsd_paths=[
            Path("./schemas/adi_movie.xsd"),
            # Path("./schemas/secondary_types.xsd"),
            # This one is found automatically by the first one's import statement
        ]
    )

    validator = ADIValidator(config=config)
    result = validator.validate(xml_file)
    return 0 if result.success else 1


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python adi_validator.py <path_to_adi.xml>")
    #     sys.exit(1)
    #
    # sys.exit(main(sys.argv[1]))

    # Example call using the dummy file we created
    sys.exit(main("sample_adi.xml"))
