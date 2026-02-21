"""
Handler for firewall filter rules.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.Rule import Rule

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class FirewallRuleHandler(EntityHandler):
    """
    Handler for firewall filter rule entities.

    Note: Firewall rules don't have a unique name field, so matching
    is done by description (primary) with source/destination/action
    as secondary keys. This can lead to ambiguous matches.
    """

    @property
    def entity_type(self) -> str:
        return "firewall_rule"

    @property
    def primary_key(self) -> str:
        return "description"  # Best available unique-ish field

    @property
    def secondary_keys(self) -> List[str]:
        return ["source_net", "destination_net", "action", "interface"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "enabled",
            "action",
            "quick",
            "interface",
            "direction",
            "ipprotocol",
            "protocol",
            "source_net",
            "source_not",
            "source_port",
            "destination_net",
            "destination_not",
            "destination_port",
            "log",
            "description"
        ]

    def fetch_all(self, client: 'BaseClient') -> List[Rule]:
        """
        Fetch all firewall rules from OPNsense across all interfaces.

        Args:
            client: OPNsense API client

        Returns:
            List of Rule entities
        """
        return client.firewall_filter_search_all_rules()

    def create(self, client: 'BaseClient', entity: Rule) -> Any:
        """
        Create a new firewall rule.

        Args:
            client: OPNsense API client
            entity: Rule entity to create

        Returns:
            API Result object
        """
        return client.firewall_filter_add_rule(entity)

    def update(self, client: 'BaseClient', uuid: str, entity: Rule) -> Any:
        """
        Update an existing firewall rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the rule to update
            entity: Updated Rule entity

        Returns:
            API Result object
        """
        return client.firewall_filter_set_rule(uuid, entity)

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a firewall rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the rule to delete

        Returns:
            API Result object
        """
        return client.firewall_filter_del_rule(uuid)

    def get_primary_key_value(self, entity: Any) -> str:
        """
        Get description as primary key.

        Args:
            entity: Rule entity

        Returns:
            Description or formatted fallback
        """
        description = getattr(entity, 'description', None)
        if description:
            return description

        # Fallback: create a descriptive key from rule attributes
        action = getattr(entity, 'action', None)
        if hasattr(action, 'value'):
            action = action.value

        source = getattr(entity, 'source_net', ['any'])
        if isinstance(source, list):
            source = ','.join(source) if source else 'any'

        dest = getattr(entity, 'destination_net', ['any'])
        if isinstance(dest, list):
            dest = ','.join(dest) if dest else 'any'

        return f"{action}:{source}->{dest}"

    def match(self, desired: Any, actual_list: List[Any]) -> tuple:
        """
        Match rules with special handling for rules without descriptions.

        Args:
            desired: The desired rule
            actual_list: List of actual rules

        Returns:
            Tuple of (match_type, matched_entity, alternatives)
        """
        desired_desc = getattr(desired, 'description', None)

        # Primary key match (description)
        if desired_desc:
            for actual in actual_list:
                actual_desc = getattr(actual, 'description', None)
                if actual_desc and actual_desc == desired_desc:
                    return ('exact', actual, [])

        # Secondary key matches
        alternatives = []
        for actual in actual_list:
            match_score = 0

            # Check action
            desired_action = getattr(desired, 'action', None)
            actual_action = getattr(actual, 'action', None)
            if desired_action and actual_action and desired_action == actual_action:
                match_score += 1

            # Check source_net
            desired_src = getattr(desired, 'source_net', None)
            actual_src = getattr(actual, 'source_net', None)
            if desired_src and actual_src and set(desired_src) == set(actual_src):
                match_score += 1

            # Check destination_net
            desired_dst = getattr(desired, 'destination_net', None)
            actual_dst = getattr(actual, 'destination_net', None)
            if desired_dst and actual_dst and set(desired_dst) == set(actual_dst):
                match_score += 1

            # Check interface
            desired_iface = getattr(desired, 'interface', None)
            actual_iface = getattr(actual, 'interface', None)
            if desired_iface and actual_iface and set(desired_iface) == set(actual_iface):
                match_score += 1

            # Need at least 3 matches to be considered a potential match
            if match_score >= 3:
                if actual not in alternatives:
                    alternatives.append(actual)

        if len(alternatives) == 1:
            return ('secondary', alternatives[0], [])
        elif len(alternatives) > 1:
            return ('ambiguous', None, alternatives)

        return ('none', None, [])

    def create_entity(self,
                      action: str = 'pass',
                      interface: List[str] = None,
                      source: str = 'any',
                      destination: str = 'any',
                      protocol: str = 'any',
                      source_port: str = None,
                      destination_port: str = None,
                      direction: str = 'in',
                      enabled: bool = True,
                      log: bool = False,
                      quick: bool = True,
                      description: str = None,
                      **kwargs) -> Rule:
        """
        Create a new Rule entity instance.

        Args:
            action: Rule action ('pass', 'block', 'reject')
            interface: List of interfaces (e.g., ['lan', 'wan'])
            source: Source network/alias (e.g., 'any', '192.168.1.0/24', 'alias_name')
            destination: Destination network/alias
            protocol: Protocol ('any', 'tcp', 'udp', 'icmp', etc.)
            source_port: Source port(s)
            destination_port: Destination port(s)
            direction: Direction ('in', 'out')
            enabled: Whether rule is enabled
            log: Whether to log matches
            quick: Whether to use quick matching
            description: Rule description (recommended for matching)

        Returns:
            Rule entity
        """
        # Convert action string to enum
        action_enum = Rule.RulesRuleActionEnum(action)

        # Convert direction string to enum
        direction_enum = Rule.RulesRuleDirectionEnum(direction)

        entity_kwargs = {
            'enabled': enabled,
            'action': action_enum,
            'direction': direction_enum,
            'protocol': protocol,
            'quick': quick,
            'log': log,
        }

        # Handle source_net
        if isinstance(source, str):
            entity_kwargs['source_net'] = [source]
        elif isinstance(source, list):
            entity_kwargs['source_net'] = source

        # Handle destination_net
        if isinstance(destination, str):
            entity_kwargs['destination_net'] = [destination]
        elif isinstance(destination, list):
            entity_kwargs['destination_net'] = destination

        if interface is not None:
            entity_kwargs['interface'] = interface
        if source_port is not None:
            entity_kwargs['source_port'] = source_port
        if destination_port is not None:
            entity_kwargs['destination_port'] = destination_port
        if description is not None:
            entity_kwargs['description'] = description

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Rule(**entity_kwargs)
