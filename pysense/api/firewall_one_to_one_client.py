from pysense.base_client import BaseClient
from pysense.pydantic.OneToOneRule import Rule as OneToOneRule
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import OneToOneRuleSearchResult


class FirewallOneToOneClient(BaseClient):
    """
    OPNsense Firewall 1:1 NAT (One-to-One NAT) API client.

    Provides CRUD operations for bidirectional NAT rules that map
    external IPs to internal hosts.
    """

    def firewall_one_to_one_search_rule(self, search: SearchRequest = None) -> OneToOneRuleSearchResult:
        """Search 1:1 NAT rules with optional filtering"""
        data = self._search('firewall/one_to_one/searchRule', search)
        return OneToOneRuleSearchResult.from_ui_dict(data, OneToOneRule)

    def firewall_one_to_one_get_rule(self, uuid: str = None) -> OneToOneRule:
        """Get a specific 1:1 NAT rule by UUID, or empty template if no UUID"""
        data = self._get('firewall/one_to_one/getRule' + self._get_arg_formatter(uuid))
        return OneToOneRule.from_ui_dict(data)

    def firewall_one_to_one_add_rule(self, rule: OneToOneRule) -> Result:
        """Create a new 1:1 NAT rule"""
        data = self._post('firewall/one_to_one/addRule', rule)
        return Result(**data)

    def firewall_one_to_one_set_rule(self, uuid: str, rule: OneToOneRule) -> Result:
        """Update an existing 1:1 NAT rule"""
        data = self._post(f'firewall/one_to_one/setRule/{uuid}', rule)
        return Result(**data)

    def firewall_one_to_one_del_rule(self, uuid: str) -> Result:
        """Delete a 1:1 NAT rule"""
        data = self._post(f'firewall/one_to_one/delRule/{uuid}', '')
        return Result(**data)

    def firewall_one_to_one_savepoint(self) -> dict:
        """Create a savepoint for rollback capability before applying changes"""
        return self._post('firewall/one_to_one/savepoint', '')

    def firewall_one_to_one_apply(self, rollback_revision: str = None) -> Result:
        """Apply pending 1:1 NAT changes, optionally with rollback revision"""
        endpoint = 'firewall/one_to_one/apply' + self._get_arg_formatter(rollback_revision)
        data = self._post(endpoint, '')
        return Result(**data)

    def firewall_one_to_one_cancel_rollback(self, rollback_revision: str) -> Result:
        """Cancel a pending rollback"""
        data = self._post(f'firewall/one_to_one/cancelRollback/{rollback_revision}', '')
        return Result(**data)
