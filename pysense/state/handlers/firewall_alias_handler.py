"""
Handler for firewall aliases.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.Alias import Alias

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class FirewallAliasHandler(EntityHandler):
    """
    Handler for firewall alias entities.

    Manages firewall aliases (hosts, networks, ports, etc.) in OPNsense.
    """

    @property
    def entity_type(self) -> str:
        return "firewall_alias"

    @property
    def primary_key(self) -> str:
        return "name"  # Alias names are unique

    @property
    def secondary_keys(self) -> List[str]:
        return ["content"]  # Could match by content if name doesn't match

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "enabled",
            "name",
            "type",
            "content",
            "description",
            "categories"
        ]

    def fetch_all(self, client: 'BaseClient') -> List[Alias]:
        """
        Fetch all firewall aliases from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of Alias entities
        """
        result = client.firewall_alias_search_item()
        return result.rows

    def create(self, client: 'BaseClient', entity: Alias) -> Any:
        """
        Create a new firewall alias.

        Args:
            client: OPNsense API client
            entity: Alias entity to create

        Returns:
            API Result object
        """
        return client.firewall_alias_add_item(entity)

    def update(self, client: 'BaseClient', uuid: str, entity: Alias) -> Any:
        """
        Update an existing firewall alias.

        Args:
            client: OPNsense API client
            uuid: UUID of the alias to update
            entity: Updated Alias entity

        Returns:
            API Result object
        """
        return client.firewall_alias_set_item(uuid, entity)

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a firewall alias.

        Args:
            client: OPNsense API client
            uuid: UUID of the alias to delete

        Returns:
            API Result object
        """
        return client.firewall_alias_del_item(uuid)

    def match(self, desired: Any, actual_list: List[Any]) -> tuple:
        """
        Override match to handle content comparison properly.

        Args:
            desired: The desired alias
            actual_list: List of actual aliases

        Returns:
            Tuple of (match_type, matched_entity, alternatives)
        """
        desired_name = getattr(desired, 'name', '') or ''

        # Primary key match (name)
        for actual in actual_list:
            actual_name = getattr(actual, 'name', '') or ''
            if actual_name and desired_name and actual_name == desired_name:
                return ('exact', actual, [])

        # Secondary key match (content)
        # Content is stored as newline-separated string
        alternatives = []
        desired_content = self._normalize_content(getattr(desired, 'content', None))

        if desired_content:
            for actual in actual_list:
                actual_content = self._normalize_content(getattr(actual, 'content', None))
                if actual_content and desired_content == actual_content:
                    if actual not in alternatives:
                        alternatives.append(actual)

        if len(alternatives) == 1:
            return ('secondary', alternatives[0], [])
        elif len(alternatives) > 1:
            return ('ambiguous', None, alternatives)

        return ('none', None, [])

    def _normalize_content(self, content: Any) -> Optional[set]:
        """
        Normalize content to a set for comparison.

        Content can be a string (newline-separated) or list.

        Args:
            content: Content value

        Returns:
            Set of content items, or None if empty
        """
        if content is None:
            return None

        if isinstance(content, str):
            items = [item.strip() for item in content.split('\n') if item.strip()]
        elif isinstance(content, list):
            items = [str(item).strip() for item in content if item]
        else:
            return None

        return set(items) if items else None

    def compute_diff(self, desired: Any, actual: Any) -> dict:
        """
        Override compute_diff to handle content comparison.

        Args:
            desired: The desired alias
            actual: The actual alias

        Returns:
            Dictionary of differences
        """
        diff = {}

        for field in self.comparable_fields:
            desired_val = getattr(desired, field, None)
            actual_val = getattr(actual, field, None)

            # Special handling for content field
            if field == 'content':
                desired_norm = self._normalize_content(desired_val)
                actual_norm = self._normalize_content(actual_val)
                if desired_norm != actual_norm:
                    diff[field] = (actual_val, desired_val)
            else:
                desired_norm = self._normalize_value(desired_val)
                actual_norm = self._normalize_value(actual_val)
                if desired_norm != actual_norm:
                    diff[field] = (actual_val, desired_val)

        return diff

    def create_entity(self, name: str, type: str, content: List[str],
                      enabled: bool = True,
                      description: Optional[str] = None,
                      categories: Optional[List[str]] = None,
                      **kwargs) -> Alias:
        """
        Create a new Alias entity instance.

        Args:
            name: Alias name (e.g., 'webservers')
            type: Alias type ('host', 'network', 'port', etc.)
            content: List of content items
            enabled: Whether the alias is enabled
            description: Optional description
            categories: Optional list of category UUIDs

        Returns:
            Alias entity
        """
        # Convert type string to enum
        type_enum = Alias.AliasesAliasTypeEnum(type)

        # Convert content list to newline-separated string
        content_str = '\n'.join(content) if content else ''

        entity_kwargs = {
            'enabled': enabled,
            'name': name,
            'type': type_enum,
            'content': content_str,
        }

        if description is not None:
            entity_kwargs['description'] = description
        if categories is not None:
            entity_kwargs['categories'] = categories

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Alias(**entity_kwargs)
