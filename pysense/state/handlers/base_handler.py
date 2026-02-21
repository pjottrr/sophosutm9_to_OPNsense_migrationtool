"""
Base handler for entity-specific state management.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class EntityHandler(ABC):
    """
    Abstract base class for entity-specific state handling.

    Each handler manages matching, fetching, and CRUD operations
    for a specific entity type (e.g., DNS hosts, DHCP reservations).
    """

    @property
    @abstractmethod
    def entity_type(self) -> str:
        """
        Return the entity type identifier.
        e.g., 'dns_host', 'dhcp_reservation', 'firewall_alias'
        """
        pass

    @property
    @abstractmethod
    def primary_key(self) -> str:
        """
        Return the primary matching field name.
        e.g., 'name', 'hostname', 'hw_address'
        """
        pass

    @property
    @abstractmethod
    def secondary_keys(self) -> List[str]:
        """
        Return fallback matching fields for ambiguous detection.
        e.g., ['ip_address', 'hw_address']
        """
        pass

    @property
    def comparable_fields(self) -> List[str]:
        """
        Return fields to compare when detecting changes.
        By default, compares all fields from the desired entity.
        Override to limit comparison to specific fields.
        """
        return []

    @property
    def read_only(self) -> bool:
        """
        Return True if this handler is read-only (compare only).
        Read-only handlers cannot create/update/delete entities automatically.
        Changes must be applied manually through the OPNsense web UI.
        """
        return False

    @abstractmethod
    def fetch_all(self, client: 'BaseClient') -> List[Any]:
        """
        Fetch all current entities from OPNsense.

        Args:
            client: The OPNsense API client

        Returns:
            List of entity objects (Pydantic models)
        """
        pass

    @abstractmethod
    def create(self, client: 'BaseClient', entity: Any) -> Any:
        """
        Create a new entity in OPNsense.

        Args:
            client: The OPNsense API client
            entity: The entity to create (Pydantic model)

        Returns:
            API Result object
        """
        pass

    @abstractmethod
    def update(self, client: 'BaseClient', uuid: str, entity: Any) -> Any:
        """
        Update an existing entity in OPNsense.

        Args:
            client: The OPNsense API client
            uuid: UUID of the entity to update
            entity: The updated entity (Pydantic model)

        Returns:
            API Result object
        """
        pass

    @abstractmethod
    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete an entity from OPNsense.

        Args:
            client: The OPNsense API client
            uuid: UUID of the entity to delete

        Returns:
            API Result object
        """
        pass

    def get_primary_key_value(self, entity: Any) -> str:
        """
        Extract the primary key value from an entity.
        Override for composite keys.

        Args:
            entity: The entity to extract the key from

        Returns:
            The primary key value as a string
        """
        return str(getattr(entity, self.primary_key, ''))

    def get_uuid(self, entity: Any) -> Optional[str]:
        """
        Extract the UUID from an entity if available.

        Args:
            entity: The entity to extract UUID from

        Returns:
            UUID string or None
        """
        uuid = getattr(entity, 'uuid', None)
        return str(uuid) if uuid else None

    def match(self, desired: Any, actual_list: List[Any]) -> Tuple[str, Optional[Any], List[Any]]:
        """
        Match a desired entity against a list of actual entities.

        Matching strategy:
        1. First try UUID match if desired entity has a UUID
        2. Then try exact primary key match
        3. If no primary match, check secondary keys for potential matches
        4. Return match type and matched entity(ies)

        Args:
            desired: The desired entity state
            actual_list: List of actual entities from OPNsense

        Returns:
            Tuple of (match_type, matched_entity, alternatives)
            - match_type: 'exact', 'uuid', 'secondary', 'ambiguous', or 'none'
            - matched_entity: The matched entity (None if ambiguous or none)
            - alternatives: List of potential matches (for ambiguous)
        """
        # UUID match (highest priority if UUID is specified)
        desired_uuid = self.get_uuid(desired)
        if desired_uuid:
            for actual in actual_list:
                actual_uuid = self.get_uuid(actual)
                if actual_uuid and desired_uuid == actual_uuid:
                    return ('uuid', actual, [])

        # Primary key match
        desired_key = self.get_primary_key_value(desired)
        for actual in actual_list:
            actual_key = self.get_primary_key_value(actual)
            if actual_key and desired_key and actual_key == desired_key:
                return ('exact', actual, [])

        # Secondary key matches (for ambiguous detection)
        alternatives = []
        for actual in actual_list:
            for key in self.secondary_keys:
                desired_val = getattr(desired, key, None)
                actual_val = getattr(actual, key, None)
                if desired_val is not None and actual_val is not None and desired_val == actual_val:
                    if actual not in alternatives:
                        alternatives.append(actual)
                    break

        if len(alternatives) == 1:
            return ('secondary', alternatives[0], [])
        elif len(alternatives) > 1:
            return ('ambiguous', None, alternatives)

        return ('none', None, [])

    def compute_diff(self, desired: Any, actual: Any) -> Dict[str, Tuple[Any, Any]]:
        """
        Compute differences between desired and actual entity states.

        Args:
            desired: The desired entity state
            actual: The actual entity state

        Returns:
            Dictionary of {field_name: (old_value, new_value)} for changed fields
        """
        diff = {}

        # Get fields to compare
        if self.comparable_fields:
            fields = self.comparable_fields
        else:
            # Compare all fields from desired entity
            fields = [f for f in desired.__class__.model_fields.keys()
                     if f not in ('uuid',)]

        for field in fields:
            desired_val = getattr(desired, field, None)
            actual_val = getattr(actual, field, None)

            # Normalize for comparison
            desired_normalized = self._normalize_value(desired_val)
            actual_normalized = self._normalize_value(actual_val)

            if desired_normalized != actual_normalized:
                diff[field] = (actual_val, desired_val)

        return diff

    def _normalize_value(self, value: Any) -> Any:
        """
        Normalize a value for comparison.
        Handles None vs empty string, lists, etc.
        """
        if value is None:
            return None
        if isinstance(value, str) and value == '':
            return None
        if isinstance(value, list) and len(value) == 0:
            return None
        return value

    def create_entity(self, **kwargs) -> Any:
        """
        Create a new entity instance with the given parameters.
        Override in subclasses to return the appropriate Pydantic model.

        Args:
            **kwargs: Entity field values

        Returns:
            A new entity instance
        """
        raise NotImplementedError(
            f"create_entity must be implemented by {self.__class__.__name__}"
        )
