from pysense.base_client import BaseClient
from pysense.pydantic.SNATRule import Rule as SNATRule
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import SNATRuleSearchResult


class FirewallSnatClient(BaseClient):

    def firewall_snat_search_rule(self, search: SearchRequest = None) -> SNATRuleSearchResult:
        data = self._search('firewall/source_nat/searchRule', search)
        return SNATRuleSearchResult.from_ui_dict(data, SNATRule)

    def firewall_snat_get_rule(self, uuid: str = None) -> SNATRule:
        data = self._get('firewall/source_nat/getRule' + self._get_arg_formatter(uuid))
        return SNATRule.from_ui_dict(data)

    def firewall_snat_add_rule(self, rule: SNATRule) -> Result:
        data = self._post('firewall/source_nat/addRule', rule)
        return Result(**data)

    def firewall_snat_set_rule(self, uuid: str, rule: SNATRule) -> Result:
        data = self._post(f'firewall/source_nat/setRule/{uuid}', rule)
        return Result(**data)

    def firewall_snat_del_rule(self, uuid: str) -> Result:
        data = self._post(f'firewall/source_nat/delRule/{uuid}', '')
        return Result(**data)

    def firewall_snat_savepoint(self) -> dict:
        return self._post('firewall/source_nat/savepoint', '')

    def firewall_snat_apply(self, rollback_revision: str = None) -> Result:
        endpoint = 'firewall/source_nat/apply' + self._get_arg_formatter(rollback_revision)
        data = self._post(endpoint, '')
        return Result(**data)

    def firewall_snat_cancel_rollback(self, rollback_revision: str) -> Result:
        data = self._post(f'firewall/source_nat/cancelRollback/{rollback_revision}', '')
        return Result(**data)
