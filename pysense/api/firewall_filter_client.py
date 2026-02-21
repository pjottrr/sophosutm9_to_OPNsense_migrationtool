from typing import List

from pysense.base_client import BaseClient
from pysense.pydantic.Rule import Rule
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import RuleSearchResult


class FirewallFilterClient(BaseClient):

    def firewall_filter_search_rule(self, search: SearchRequest = None) -> RuleSearchResult:
        data = self._search('firewall/filter/searchRule', search)
        return RuleSearchResult.from_ui_dict(data, Rule)

    def firewall_filter_search_rule_by_interface(self, interface: str) -> RuleSearchResult:
        """
        Search firewall filter rules for a specific interface.

        Args:
            interface: Interface identifier (e.g., 'lan', 'wan', 'opt1')

        Returns:
            RuleSearchResult with rules for that interface
        """
        data = self._post('firewall/filter/searchRule', {
            'current': 1,
            'rowCount': -1,  # All rows
            'sort': {},
            'searchPhrase': '',
            'interface': interface
        })
        return RuleSearchResult.from_ui_dict(data, Rule)

    def firewall_filter_search_all_rules(self) -> List[Rule]:
        """
        Fetch all firewall filter rules across all interfaces.

        OPNsense filter rules are organized per interface, so this method:
        1. Fetches all assigned interfaces
        2. Searches for rules on each interface using the interface parameter
        3. Combines results, removing duplicates by UUID

        Returns:
            List of all Rule entities across all interfaces
        """
        # Get all assigned interfaces
        interfaces = self.interface_overview_export()
        assigned = interfaces.get_assigned()

        all_rules = {}  # Use dict to deduplicate by UUID

        for iface in assigned:
            if not iface.identifier:
                continue

            try:
                result = self.firewall_filter_search_rule_by_interface(iface.identifier)

                for rule in result.rows:
                    if rule.uuid and rule.uuid not in all_rules:
                        all_rules[rule.uuid] = rule
            except Exception:
                # Skip interfaces that fail (e.g., no rules configured)
                continue

        return list(all_rules.values())

    def firewall_filter_get_rule(self, uuid: str = None) -> Rule:
        data = self._get('firewall/filter/getRule' + self._get_arg_formatter(uuid))
        return Rule.from_ui_dict(data)

    def firewall_filter_add_rule(self, rule: Rule) -> Result:
        data = self._post('firewall/filter/addRule', rule)
        return Result(**data)

    def firewall_filter_set_rule(self, uuid: str, rule: Rule) -> Result:
        data = self._post(f'firewall/filter/setRule/{uuid}', rule)
        return Result(**data)

    def firewall_filter_del_rule(self, uuid: str) -> Result:
        data = self._post(f'firewall/filter/delRule/{uuid}', '')
        return Result(**data)

    def firewall_filter_savepoint(self) -> dict:
        return self._post('firewall/filter/savepoint', '')

    def firewall_filter_apply(self, rollback_revision: str = None) -> Result:
        endpoint = 'firewall/filter/apply' + self._get_arg_formatter(rollback_revision)
        data = self._post(endpoint, '')
        return Result(**data)

    def firewall_filter_cancel_rollback(self, rollback_revision: str) -> Result:
        data = self._post(f'firewall/filter/cancelRollback/{rollback_revision}', '')
        return Result(**data)
