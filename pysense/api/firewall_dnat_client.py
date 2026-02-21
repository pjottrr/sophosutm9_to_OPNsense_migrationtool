from pysense.base_client import BaseClient
from pysense.pydantic.DNATRule import Rule as DNATRule
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import DNATRuleSearchResult


class FirewallDnatClient(BaseClient):
    """Client for OPNsense DNAT (Destination NAT / Port Forward) API."""

    def firewall_dnat_search_rule(self, search: SearchRequest = None) -> DNATRuleSearchResult:
        """
        Search DNAT (port forward) rules.

        Args:
            search: Optional search parameters

        Returns:
            DNATRuleSearchResult with matching rules
        """
        data = self._search('firewall/d_nat/searchRule', search)
        return DNATRuleSearchResult.from_ui_dict(data, DNATRule)

    def firewall_dnat_get_rule(self, uuid: str = None) -> DNATRule:
        """
        Get a specific DNAT rule by UUID.

        Args:
            uuid: UUID of the rule (optional, returns template if None)

        Returns:
            DNATRule entity
        """
        data = self._get('firewall/d_nat/getRule' + self._get_arg_formatter(uuid))
        return DNATRule.from_ui_dict(data)

    def firewall_dnat_add_rule(self, rule: DNATRule) -> Result:
        """
        Add a new DNAT (port forward) rule.

        Args:
            rule: DNATRule entity to create

        Returns:
            Result with UUID of created rule
        """
        data = self._post('firewall/d_nat/addRule', rule)
        return Result(**data)

    def firewall_dnat_set_rule(self, uuid: str, rule: DNATRule) -> Result:
        """
        Update an existing DNAT rule.

        Args:
            uuid: UUID of the rule to update
            rule: Updated DNATRule entity

        Returns:
            Result object
        """
        data = self._post(f'firewall/d_nat/setRule/{uuid}', rule)
        return Result(**data)

    def firewall_dnat_del_rule(self, uuid: str) -> Result:
        """
        Delete a DNAT rule.

        Args:
            uuid: UUID of the rule to delete

        Returns:
            Result object
        """
        data = self._post(f'firewall/d_nat/delRule/{uuid}', '')
        return Result(**data)

    def firewall_dnat_toggle_rule(self, uuid: str, disabled: bool = None) -> Result:
        """
        Toggle a DNAT rule's enabled state.

        Args:
            uuid: UUID of the rule to toggle
            disabled: Optional explicit state (True=disabled, False=enabled)

        Returns:
            Result object
        """
        endpoint = f'firewall/d_nat/toggleRule/{uuid}'
        if disabled is not None:
            endpoint += f'/{1 if disabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    def firewall_dnat_move_rule_before(self, selected_uuid: str, target_uuid: str) -> dict:
        """
        Move a DNAT rule before another rule.

        Args:
            selected_uuid: UUID of rule to move
            target_uuid: UUID of target rule (selected will be placed before this)

        Returns:
            API response dict
        """
        return self._get(f'firewall/d_nat/moveRuleBefore/{selected_uuid},{target_uuid}')

    def firewall_dnat_savepoint(self) -> dict:
        """
        Create a savepoint for DNAT rules (for rollback).

        Returns:
            Savepoint revision info
        """
        return self._post('firewall/d_nat/savepoint', '')

    def firewall_dnat_apply(self, rollback_revision: str = None) -> Result:
        """
        Apply DNAT rule changes.

        Args:
            rollback_revision: Optional rollback revision

        Returns:
            Result object
        """
        endpoint = 'firewall/d_nat/apply' + self._get_arg_formatter(rollback_revision)
        data = self._post(endpoint, '')
        return Result(**data)

    def firewall_dnat_cancel_rollback(self, rollback_revision: str) -> Result:
        """
        Cancel a pending DNAT rollback.

        Args:
            rollback_revision: Rollback revision to cancel

        Returns:
            Result object
        """
        data = self._post(f'firewall/d_nat/cancelRollback/{rollback_revision}', '')
        return Result(**data)
