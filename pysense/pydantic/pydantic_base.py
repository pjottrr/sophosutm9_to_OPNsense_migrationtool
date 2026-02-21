"""
Base classes and mixins for Pydantic models.

This module provides reusable functionality for generated Pydantic models.
"""
import types
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, field_serializer, Field
from typing import Any, Dict, Union, List, Type, Optional, get_origin, get_args, T


class BoolAsIntMixin(BaseModel):
    """
    Mixin that serializes boolean fields as "0" or "1" strings.

    When a Pydantic model inherits from this mixin, all boolean fields
    will be automatically serialized as "1" (for True) or "0" (for False)
    when using model_dump() or model_dump_json().

    Usage:
        class MyModel(BaseModel, BoolAsIntMixin):
            enabled: bool = False
            active: bool = True

        obj = MyModel()
        obj.model_dump()  # {'enabled': '0', 'active': '1'}

    Type checking:
        if isinstance(obj, BoolAsIntMixin):
            # Object supports bool-as-int serialization
            data = obj.model_dump()
    """

    @field_serializer('*', check_fields=False)
    def serialize_bools_as_int(self, value: Any, _info) -> Any:
        """Serialize boolean values as '1' or '0' strings."""
        if isinstance(value, bool):
            return "1" if value else "0"
        return value


class UIAwareMixin(BaseModel):
    uuid: Union[UUID, str] = Field(default=None, description='Unique ID for this object. Not all api calls return it. Internal aliases may use name instead of UUID.')
    # --- UIAwareMixin: _get_selected_value (Unchanged but included for context) ---
    @staticmethod
    def _get_selected_value(field_key: str, data: Dict[str, Any]) -> Union[List[str], None]:
        field_data = data.get(field_key)

        if isinstance(field_data, dict):
            selected_keys = []
            for key, value_obj in field_data.items():
                if isinstance(value_obj, dict) and value_obj.get("selected") in ["1", 1]:
                    if key:
                        selected_keys.append(key)
            return selected_keys if selected_keys else None

        if isinstance(field_data, list):
            return field_data if field_data else None

        return None

    # --- UIAwareMixin: from_ui_dict (FIXED) ---
    @classmethod
    def from_ui_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        model_key = cls.__name__.lower()
        if data.get(model_key) and isinstance(data[model_key], dict):
            data = data[model_key]

        pydantic_input = {}
        field_names = cls.model_fields.keys()

        for key in field_names:
            field_info = cls.model_fields[key]
            raw_value = data.get(key)

            value = None

            field_type = field_info.annotation
            is_list_field = get_origin(field_type) in (list, List)

            # 1. UI selection dict handling
            if isinstance(raw_value, dict):
                extracted_list = cls._get_selected_value(key, data)

                if is_list_field:
                    value = extracted_list
                elif extracted_list is not None and isinstance(extracted_list, list):
                    value = extracted_list[0] if extracted_list else None
                else:
                    value = extracted_list

            # 2. Direct value / coercion
            else:
                if raw_value in ("", None) or (isinstance(raw_value, list) and not raw_value):
                    value = None
                else:
                    if is_list_field and not isinstance(raw_value, list):
                        value = [raw_value]
                    else:
                        value = raw_value

            if value is not None:
                # numeric string → int
                if isinstance(value, str) and field_info.annotation in (int, Optional[int]):
                    try:
                        pydantic_input[key] = int(value)
                    except ValueError:
                        pydantic_input[key] = value
                else:
                    pydantic_input[key] = value

        return cls(**pydantic_input)

    # --- UIAwareMixin: to_simple_dict (Enhanced to handle UUID) ---
    def to_simple_dict(self, exclude_field_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Exports the model instance to the target simplified API dictionary format,
        converting lists (including Enum lists) to comma-separated strings.
        """
        if exclude_field_names is None:
            exclude_field_names = ["id", "uuid"]

        # Use by_alias=False to get data with Python field names for lookup
        data = self.model_dump(by_alias=False, exclude_defaults=False, exclude_none=False)

        final_data = {}
        field_names = set(self.__class__.model_fields.keys())

        for key in field_names:
            if key in exclude_field_names:
                continue

            value = data.get(key)

            # Get the output key - use serialization_alias if defined, otherwise use field name
            field_info = self.__class__.model_fields[key]
            output_key = field_info.serialization_alias if field_info.serialization_alias else key

            if isinstance(value, list):
                if value and isinstance(value[0], Enum):
                    final_data[output_key] = ",".join(v.value for v in value)
                elif value and isinstance(value[0], UUID):
                    final_data[output_key] = ",".join(str(v) for v in value)
                else:
                    final_data[output_key] = ",".join(str(v) for v in value)
            elif value is None or value == "":
                # Map missing optional values and None to empty string ""
                final_data[output_key] = ""
            elif isinstance(value, bool):
                final_data[output_key] = "1" if value else "0"
            elif isinstance(value, Enum):
                final_data[output_key] = value.value
            elif isinstance(value, UUID):
                final_data[output_key] = str(value)
            else:
                final_data[output_key] = str(value)

        return {self.__class__.__name__.lower(): final_data}

    @classmethod
    def _try_convert_value(cls, item: str, target_type: Type) -> Any:
        """
        Helper method to attempt converting a string to the target type.
        Returns the converted value or None if conversion fails.
        """
        # Handle UUID
        if target_type is UUID:
            try:
                return UUID(item)
            except (ValueError, AttributeError):
                return None

        # Handle Enum
        if isinstance(target_type, type) and issubclass(target_type, Enum):
            try:
                return target_type(item)
            except (ValueError, KeyError):
                return None

        # Handle int
        if target_type is int:
            try:
                return int(item)
            except ValueError:
                return None

        # Handle str (always succeeds)
        if target_type is str:
            return item

        # Try direct type conversion as fallback
        try:
            return target_type(item)
        except (ValueError, TypeError):
            return None

    @classmethod
    def from_basic_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Loads a model instance from the simplified dict produced by to_simple_dict().
        Fully reverses all lossy conversions:
          - comma-strings back to lists (supports List[str|UUID] and other Union types)
          - "1"/"0" back to bool
          - "" back to None
          - enum values back to Enum members
          - numeric strings back to ints
          - UUID strings back to UUID objects
        """

        if not data:
            return None
        # unwrap { "action": {...} }
        model_key = cls.__name__.lower()
        if model_key in data and isinstance(data[model_key], dict):
            data = data[model_key]

        # Build alias to field name mapping
        alias_to_field = {}
        for field_name, field_info in cls.model_fields.items():
            if field_info.serialization_alias:
                alias_to_field[field_info.serialization_alias] = field_name
            alias_to_field[field_name] = field_name  # Also map field name to itself

        result = {}
        for key, value in data.items():
            # Resolve alias to field name
            field_name = alias_to_field.get(key)
            if not field_name:
                continue
            field_info = cls.model_fields.get(field_name)
            if not field_info:
                continue

            field_type = field_info.annotation
            origin = get_origin(field_type)

            # Handle empty string → None or empty list
            if value == "":
                if origin in (list, List):
                    result[field_name] = []
                else:
                    result[field_name] = None
                continue

            # Handle comma-separated lists (including Union types like str|UUID)
            if isinstance(value, str) and origin in (list, List):
                item_type = get_args(field_type)[0]
                items = value.split(",")

                # Check if item_type is a Union (supports both Union[...] and T | U syntax)
                if get_origin(item_type) in (Union, types.UnionType):
                    union_args = [t for t in get_args(item_type) if t is not type(None)]

                    # Try to convert each item using the union types in order
                    converted_items = []
                    for item in items:
                        converted = None
                        for union_type in union_args:
                            converted = cls._try_convert_value(item, union_type)
                            if converted is not None:
                                break

                        # If no conversion succeeded, use the raw string
                        if converted is None:
                            converted = item

                        converted_items.append(converted)

                    result[field_name] = converted_items

                # Handle single type (Enum, UUID, str, int, etc.)
                else:
                    # Handle Enum
                    if isinstance(item_type, type) and issubclass(item_type, Enum):
                        result[field_name] = [item_type(item) for item in items]
                    # Handle UUID
                    elif item_type is UUID:
                        result[field_name] = [UUID(item) for item in items]
                    # Handle int
                    elif item_type is int:
                        result[field_name] = [int(item) for item in items]
                    # Handle str or other types
                    else:
                        result[field_name] = [item_type(item) for item in items]

                continue

            # Handle bools "1" / "0"
            if value in ("0", "1") and (field_type is bool or field_type == Optional[bool]):
                result[field_name] = value == "1"
                continue

            # Handle enums
            if isinstance(value, str) and isinstance(field_type, type) and issubclass(field_type, Enum):
                result[field_name] = field_type(value)
                continue

            # Handle UUID
            if isinstance(value, str) and field_type is UUID:
                try:
                    result[field_name] = UUID(value)
                    continue
                except ValueError:
                    pass

            # Handle ints
            if isinstance(value, str) and field_type in (int, Optional[int]):
                try:
                    result[field_name] = int(value)
                    continue
                except ValueError:
                    pass

            # Default
            result[field_name] = value

        return cls(**result)


# class StringBoolMixin(BaseModel):
#     """
#     Mixin for models that store boolean values as "0"/"1" strings internally.
#
#     This is useful when you need __dict__ to contain "0"/"1" strings directly
#     instead of Python bool values.
#
#     Note: When using this approach, fields should be defined as str type
#     with appropriate validation.
#     """
#     pass

# Future mixins can be added here as needed
# class DateFormatMixin(BaseModel):
#     """Mixin for standardized date formatting."""
#     pass
#
# class EnumValidationMixin(BaseModel):
#     """Mixin for enum field validation."""
#     pass