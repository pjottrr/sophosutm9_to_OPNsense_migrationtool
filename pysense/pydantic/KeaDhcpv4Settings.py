from typing import Optional, Dict, Any
from pysense.pydantic.pydantic_base import UIAwareMixin
from pysense.pydantic.General import General, DhcpSocketTypeEnum


class Dhcpv4(UIAwareMixin):
    """
    Model for Kea DHCPv4 Settings wrapper
    """
    general: Optional[General] = None

    @classmethod
    def from_ui_dict(cls, data: Dict[str, Any]) -> 'Dhcpv4':
        """Parse Dhcpv4 settings from API response"""
        # Handle wrapped response: {"dhcpv4": {...}}
        if 'dhcpv4' in data:
            data = data['dhcpv4']

        result = {}
        if 'general' in data:
            result['general'] = General.from_ui_dict({'general': data['general']})

        return cls(**result)

    def to_simple_dict(self, exclude_field_names=None):
        """Override to handle nested General model"""
        result = {}
        if self.general is not None:
            general_dict = self.general.to_simple_dict(exclude_field_names)
            result['general'] = general_dict.get('general', general_dict)
        return {'dhcpv4': result}


# Aliases
KeaDhcpv4 = Dhcpv4
