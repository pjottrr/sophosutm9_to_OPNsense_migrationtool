from typing import Generic, TypeVar, List, Dict, Any, Type

from pysense.pydantic.Account import Account
from pysense.pydantic.Action import Action
from pysense.pydantic.Alias import Alias
from pysense.pydantic.ApiUser import ApiUser
from pysense.pydantic.BaseObject import BaseObject
from pysense.pydantic.Ca import Ca
from pysense.pydantic.Category import Category
from pysense.pydantic.Cert import Cert
from pysense.pydantic.CertBase import CertBase
from pysense.pydantic.Certificate import Certificate
from pysense.pydantic.Group import Group
from pysense.pydantic.Lua import Lua
from pysense.pydantic.Rule import Rule
from pysense.pydantic.SNATRule import Rule as SNATRule
from pysense.pydantic.OneToOneRule import Rule as OneToOneRule
from pysense.pydantic.DNATRule import Rule as DNATRule
from pysense.pydantic.User import User
from pysense.pydantic.Vlan import Vlan
from pysense.pydantic.KeaDhcpv4 import Subnet4, Reservation, Peer
from pysense.pydantic.Unbound import Acl as UnboundAcl, Blocklist, Dot, Alias as UnboundAlias, Host as UnboundHost
from pysense.pydantic.Validation import Validation
from pysense.pydantic.pydantic_base import UIAwareMixin

T = TypeVar('T')
class SearchResult(UIAwareMixin, Generic[T]):
    rows: List[T]
    rowCount: int
    total: int
    current: int

    @classmethod
    def from_ui_dict(cls, data: Dict[str, Any], row_type: Type[T]) -> 'SearchResult[T]':
        """Parse SearchResult from dict, converting each row dict to typed object"""
        parsed_rows = [row_type.from_ui_dict(row_dict) for row_dict in data['rows']]
        return cls(
            rows=parsed_rows,
            rowCount=data['rowCount'],
            total=data['total'],
            current=data['current']
        )

    @classmethod
    def from_basic_dict(cls, data: Dict[str, Any], row_type: Type[T]) -> 'SearchResult[T]':
        """Parse SearchResult from dict, converting each row dict to typed object"""
        parsed_rows = [row_type.from_basic_dict(row_dict) for row_dict in data['rows']]
        return cls(
            rows=parsed_rows,
            rowCount=data['rowCount'],
            total=data['total'],
            current=data['current']
        )

    def get_by(self, key, value) -> T:
        for row in self.rows:
            if getattr(row,key) == value:
                return row
        return None

    def get_by_name(self, name) -> T:
        return self.get_by('name', name)

BaseObjectSearchResult = SearchResult[BaseObject]
CertSearchResult = SearchResult[Cert]
RuleSearchResult = SearchResult[Rule]
AliasSearchResult = SearchResult[Alias]
CategorySearchResult = SearchResult[Category]
ActionSearchResult = SearchResult[Action]
CertificateSearchResult = SearchResult[Certificate]
CaSearchResult = SearchResult[Ca]
CertBaseSearchResult = SearchResult[CertBase]
AccountSearchResult = SearchResult[Account]
ValidationSearchResult = SearchResult[Validation]
LuaSearchResult = SearchResult[Lua]
UserSearchResult = SearchResult[User]
GroupSearchResult = SearchResult[Group]
ApiUserSearchResult = SearchResult[ApiUser]
SNATRuleSearchResult = SearchResult[SNATRule]
OneToOneRuleSearchResult = SearchResult[OneToOneRule]
VlanSearchResult = SearchResult[Vlan]
Subnet4SearchResult = SearchResult[Subnet4]
ReservationSearchResult = SearchResult[Reservation]
PeerSearchResult = SearchResult[Peer]
UnboundAclSearchResult = SearchResult[UnboundAcl]
UnboundBlocklistSearchResult = SearchResult[Blocklist]
UnboundDotSearchResult = SearchResult[Dot]
UnboundAliasSearchResult = SearchResult[UnboundAlias]
UnboundHostSearchResult = SearchResult[UnboundHost]
DNATRuleSearchResult = SearchResult[DNATRule]
