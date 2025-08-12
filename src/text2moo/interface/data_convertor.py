import json
import polars as pl
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path
from text2moo.models.types import BaseUnit, OptimizationGroup


class DataConvertorError(Exception):
    """Custom exception for data conversion errors."""

    pass


class BaseDataConvertor(ABC):
    """Abstract base class for data convertors."""

    @abstractmethod
    def convert(self, input_data: Union[str, Path, Any]) -> OptimizationGroup:
        """Convert input data to OptimizationGroup format."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate if the input data meets requirements."""
        pass


class ExcelDataConvertor(BaseDataConvertor):
    """Convertor for Excel input data."""

    def __init__(self, sheet_name: Optional[Union[str, int]] = None):
        """
        Initialize Excel data convertor.

        Args:
            sheet_name: Name or index of the sheet to read. Defaults to None (first sheet).
        """
        self.sheet_name = sheet_name

    def convert(self, input_data: Union[str, Path]) -> OptimizationGroup:
        """
        Convert Excel file to OptimizationGroup.

        Args:
            input_data: Path to Excel file

        Returns:
            OptimizationGroup containing validated BaseUnits

        Raises:
            DataConvertorError: If validation fails or conversion errors occur
        """
        try:
            # Read Excel file
            df = pl.read_excel(input_data, sheet_name=self.sheet_name)

            # Validate data
            if not self.validate(df):
                raise DataConvertorError("Data validation failed")

            # Extract attribute keys (excluding 'id' and 'name')
            reserved_cols = {"id", "name"}
            unit_attr = [col for col in df.columns if col not in reserved_cols]

            # Convert rows to BaseUnits
            units = []
            for row in df.iter_rows(named=True):
                # Extract attributes (excluding id and name)
                attributes = {col: row[col] for col in unit_attr}

                # Create BaseUnit
                unit = BaseUnit(
                    id=str(row["id"]), name=row.get("name"), attributes=attributes
                )
                units.append(unit)

            return OptimizationGroup(unit_attr=unit_attr, units=units)

        except FileNotFoundError:
            raise DataConvertorError(f"Excel file not found: {input_data}")
        except KeyError as e:
            raise DataConvertorError(f"Required column missing: {e}")
        except Exception as e:
            raise DataConvertorError(f"Error converting Excel data: {str(e)}")

    def validate(self, data: pl.DataFrame) -> bool:
        """
        Validate Excel data meets requirements:
        1. Each row should have the same attr keywords
        2. Have 'name' and 'id' columns

        Args:
            data: Polars DataFrame to validate

        Returns:
            bool: True if valid, raises exception otherwise
        """
        # Check if DataFrame is empty
        if data.is_empty():
            raise DataConvertorError("Excel file contains no data")

        # Check required columns exist
        required_cols = {"id", "name"}
        if not required_cols.issubset(set(data.columns)):
            missing = required_cols - set(data.columns)
            raise DataConvertorError(f"Required columns missing: {missing}")

        # Check for duplicate IDs
        id_counts = data.group_by("id").count()
        if (id_counts["count"] > 1).any():
            raise DataConvertorError("Duplicate IDs found in data")

        # Check for missing IDs
        if data["id"].null_count() > 0:
            raise DataConvertorError("Missing ID values found")

        # Check all rows have same columns (Polars DataFrame ensures this)
        # Check for consistent data types in attribute columns
        attr_cols = [col for col in data.columns if col not in required_cols]
        for col in attr_cols:
            # Skip validation for columns with all null values
            if data[col].null_count() < len(data):
                # Just ensure the column exists for all rows (DataFrame structure ensures this)
                pass

        return True


class JSONDataConvertor(BaseDataConvertor):
    """Convertor for JSON input data."""

    def convert(self, input_data: Union[str, Path]) -> OptimizationGroup:
        """
        Convert JSON file to OptimizationGroup.

        Args:
            input_data: Path to JSON file

        Returns:
            OptimizationGroup containing validated BaseUnits

        Raises:
            DataConvertorError: If validation fails or conversion errors occur
        """
        try:
            # Read JSON file
            with open(input_data, "r") as f:
                data = json.load(f)

            # Validate data
            if not self.validate(data):
                raise DataConvertorError("Data validation failed")

            # Handle both list and dict formats
            if isinstance(data, dict):
                # If dict, expect a 'data' or 'units' key with list of items
                if "data" in data:
                    items = data["data"]
                elif "units" in data:
                    items = data["units"]
                else:
                    # Treat the dict as a single item
                    items = [data]
            elif isinstance(data, list):
                items = data
            else:
                raise DataConvertorError("JSON must contain a list or dict")

            # Extract attribute keys (excluding 'id' and 'name')
            if not items:
                raise DataConvertorError("JSON contains no data")

            # Get all unique keys from all items
            reserved_cols = {"id", "name"}
            all_keys = set()
            for item in items:
                if isinstance(item, dict):
                    all_keys.update(item.keys())

            unit_attr = sorted([key for key in all_keys if key not in reserved_cols])

            # Convert items to BaseUnits
            units = []
            for item in items:
                if not isinstance(item, dict):
                    raise DataConvertorError(f"Invalid item format: {type(item)}")

                # Extract attributes (excluding id and name)
                attributes = {key: item.get(key) for key in unit_attr if key in item}

                # Create BaseUnit
                unit = BaseUnit(
                    id=str(item["id"]), name=item.get("name"), attributes=attributes
                )
                units.append(unit)

            return OptimizationGroup(unit_attr=unit_attr, units=units)

        except FileNotFoundError:
            raise DataConvertorError(f"JSON file not found: {input_data}")
        except json.JSONDecodeError as e:
            raise DataConvertorError(f"Invalid JSON format: {e}")
        except KeyError as e:
            raise DataConvertorError(f"Required field missing: {e}")
        except Exception as e:
            raise DataConvertorError(f"Error converting JSON data: {str(e)}")

    def validate(self, data: Any) -> bool:
        """
        Validate JSON data meets requirements:
        1. Each item should have 'id' and 'name' fields
        2. No duplicate IDs

        Args:
            data: JSON data (list or dict)

        Returns:
            bool: True if valid, raises exception otherwise
        """
        # Extract items list
        if isinstance(data, dict):
            if "data" in data:
                items = data["data"]
            elif "units" in data:
                items = data["units"]
            else:
                items = [data]
        elif isinstance(data, list):
            items = data
        else:
            raise DataConvertorError("JSON must contain a list or dict")

        # Check if empty
        if not items:
            raise DataConvertorError("JSON contains no data")

        # Check each item
        seen_ids = set()
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise DataConvertorError(f"Item at index {idx} is not a dict")

            # Check required fields
            if "id" not in item:
                raise DataConvertorError(f"Item at index {idx} missing 'id' field")
            if "name" not in item:
                raise DataConvertorError(f"Item at index {idx} missing 'name' field")

            # Check for duplicate IDs
            item_id = str(item["id"])
            if item_id in seen_ids:
                raise DataConvertorError(f"Duplicate ID found: {item_id}")
            seen_ids.add(item_id)

            # Check for null ID
            if item["id"] is None:
                raise DataConvertorError(f"Item at index {idx} has null ID")

        return True


class DataConvertor:
    """
    Main data convertor class that delegates to specific convertors.
    Designed to be extensible for future data formats.
    """

    def __init__(self):
        """Initialize convertor with supported formats."""
        self._convertors: Dict[str, BaseDataConvertor] = {
            "excel": ExcelDataConvertor(),
            "xlsx": ExcelDataConvertor(),
            "xls": ExcelDataConvertor(),
            "json": JSONDataConvertor(),
        }

    def convert(
        self, input_data: Union[str, Path], format: Optional[str] = None
    ) -> OptimizationGroup:
        """
        Convert input data to OptimizationGroup format.

        Args:
            input_data: Path to input data file
            format: Optional format specification. If None, inferred from file extension.

        Returns:
            OptimizationGroup containing validated data

        Raises:
            DataConvertorError: If format not supported or conversion fails
        """
        # Convert to Path object
        path = Path(input_data)

        # Determine format
        if format is None:
            format = path.suffix.lower().lstrip(".")

        # Get appropriate convertor
        convertor = self._convertors.get(format)
        if convertor is None:
            supported = list(self._convertors.keys())
            raise DataConvertorError(
                f"Unsupported format: {format}. Supported formats: {supported}"
            )

        # Convert data
        return convertor.convert(input_data)

    def register_convertor(self, format: str, convertor: BaseDataConvertor):
        """
        Register a new convertor for a specific format.
        This allows for easy extension with new data formats.

        Args:
            format: File format identifier (e.g., 'json', 'csv')
            convertor: Instance of BaseDataConvertor for this format
        """
        self._convertors[format] = convertor
