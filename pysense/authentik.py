import requests
from typing import Dict, Any


class AuthentikConfigurator:
    def __init__(self, base_url: str, token: str):
        """
        Initialize the Authentik configurator

        Args:
            base_url: Authentik instance URL (e.g., 'https://auth.example.com')
            token: API token from Authentik admin interface
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API request to Authentik"""
        url = f"{self.base_url}/api/v3/{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def get_or_create_group(self, group_name: str, group_attributes: Dict = None) -> str:
        """
        Get existing group or create a new one

        Args:
            group_name: Name of the group
            group_attributes: Optional attributes for the group

        Returns:
            Group UUID
        """
        # Check if group already exists
        print(f"Checking for existing group: {group_name}")
        try:
            groups = self._make_request('GET', f'core/groups/?name={group_name}')
            if groups['results']:
                group_uuid = groups['results'][0]['pk']
                print(f"✓ Found existing group with UUID: {group_uuid}")
                return group_uuid
        except Exception as e:
            print(f"Error checking for existing group: {e}")

        # Create new group if not found
        data = {
            "name": group_name,
            "is_superuser": False,
            "attributes": group_attributes or {}
        }

        print(f"Creating group: {group_name}")
        result = self._make_request('POST', 'core/groups/', data)
        group_uuid = result['pk']
        print(f"✓ Group created with UUID: {group_uuid}")
        return group_uuid

    def get_default_flows(self) -> Dict[str, str]:
        """Get default authorization and invalidation flows"""
        flows = self._make_request('GET', 'flows/instances/')

        auth_flow = None
        invalidation_flow = None

        for flow in flows['results']:
            if flow['designation'] == 'authorization' and 'default-provider-authorization-implicit-consent' in flow[
                'slug']:
                auth_flow = flow['pk']
            elif flow['designation'] == 'invalidation' and 'default-provider-invalidation-flow' in flow['slug']:
                invalidation_flow = flow['pk']

        return {
            'authorization_flow': auth_flow,
            'invalidation_flow': invalidation_flow
        }

    def get_or_create_proxy_provider(self,
                                     provider_name: str,
                                     external_host: str,
                                     internal_host: str = None,
                                     skip_path_regex: str = None,
                                     cookie_domain: str = None,
                                     authorization_flow: str = None,
                                     invalidation_flow: str = None) -> int:
        """
        Get existing proxy provider or create a new one

        Args:
            provider_name: Name of the provider
            external_host: External URL that users will access
            internal_host: Internal URL to proxy to (defaults to external_host)
            skip_path_regex: Optional regex for paths to skip authentication
            cookie_domain: Optional cookie domain for auth (e.g., '.example.com')
            authorization_flow: UUID of authorization flow (auto-detected if None)
            invalidation_flow: UUID of invalidation flow (auto-detected if None)

        Returns:
            Provider ID
        """
        # Check if provider already exists
        print(f"Checking for existing proxy provider: {provider_name}")
        try:
            providers = self._make_request('GET', f'providers/proxy/?name={provider_name}')
            for provider in providers.get('results', []):
                if provider.get('name') == provider_name:
                    provider_id = provider['pk']
                    print(f"✓ Found existing proxy provider with ID: {provider_id}")
                    return provider_id
        except Exception as e:
            print(f"Error checking for existing provider: {e}")

        # Create new provider if not found
        # Get default flows if not provided
        if not authorization_flow or not invalidation_flow:
            flows = self.get_default_flows()
            authorization_flow = authorization_flow or flows['authorization_flow']
            invalidation_flow = invalidation_flow or flows['invalidation_flow']

        if not authorization_flow or not invalidation_flow:
            raise ValueError(
                "Could not find default flows. Please specify authorization_flow and invalidation_flow manually.")

        data = {
            "name": provider_name,
            "authorization_flow": authorization_flow,
            "invalidation_flow": invalidation_flow,
            "external_host": external_host,
            "internal_host": internal_host or external_host,
            "mode": "forward_domain",  # Use forward_domain for forward auth
            "skip_path_regex": skip_path_regex or "",
            "basic_auth_enabled": False,
            "basic_auth_password_attribute": "",
            "basic_auth_user_attribute": "",
            "certificate": None,
            "cookie_domain": cookie_domain or "",
            "jwks_sources": [],
            "access_token_validity": "minutes=10"
        }

        print(f"Creating proxy provider: {provider_name}")
        result = self._make_request('POST', 'providers/proxy/', data)
        provider_id = result['pk']
        print(f"✓ Proxy provider created with ID: {provider_id}")
        return provider_id

    def get_or_create_application(self,
                                  app_name: str,
                                  app_slug: str,
                                  provider_id: int,
                                  policy_engine_mode: str = "all") -> str:
        """
        Get existing application or create a new one

        Args:
            app_name: Display name of the application
            app_slug: URL slug for the application
            provider_id: ID of the provider to associate
            policy_engine_mode: Policy engine mode ("all", "any")

        Returns:
            Application UUID
        """
        # Check if application already exists (by slug)
        print(f"Checking for existing application: {app_name} (slug: {app_slug})")
        try:
            apps = self._make_request('GET', f'core/applications/?ordering=name&page=1&page_size=100&search={app_slug}&superuser_full_list=true')
            for app in apps.get('results', []):
                if app.get('slug') == app_slug:
                    app_uuid = app['pk']
                    print(f"✓ Found existing application with UUID: {app_uuid}")

                    # Update provider association if different
                    if app.get('provider') != provider_id:
                        print(f"Updating application provider association")
                        update_data = {
                            "name": app_name,
                            "slug": app_slug,
                            "provider": provider_id,
                            "policy_engine_mode": policy_engine_mode,
                            "meta_launch_url": app.get('meta_launch_url', ''),
                            "meta_description": app.get('meta_description', f"Application for {app_name}"),
                            "meta_publisher": app.get('meta_publisher', ''),
                            "open_in_new_tab": app.get('open_in_new_tab', True)
                        }
                        self._make_request('PUT', f'core/applications/{app_uuid}/', update_data)
                        print(f"✓ Application provider updated")

                    return app_uuid
        except Exception as e:
            print(f"Error checking for existing application: {e}")

        # Create new application if not found
        data = {
            "name": app_name,
            "slug": app_slug,
            "provider": provider_id,
            "policy_engine_mode": policy_engine_mode,
            "meta_launch_url": "",
            "meta_description": f"Application for {app_name}",
            "meta_publisher": "",
            "open_in_new_tab": True
        }

        print(f"Creating application: {app_name}")
        result = self._make_request('POST', 'core/applications/', data)
        app_uuid = result['pk']
        print(f"✓ Application created with UUID: {app_uuid}")
        return app_uuid

    def get_or_create_group_binding(self,
                                    target_uuid: str,
                                    group_uuid: str,
                                    order: int = 0) -> str:
        """
        Get existing group binding or create a new one

        Args:
            target_uuid: Target UUID (application, flow, etc.)
            group_uuid: Group UUID to bind to the target
            order: Binding order (lower numbers execute first)

        Returns:
            Binding UUID
        """
        # Check if binding already exists
        print(f"Checking for existing group binding")
        try:
            bindings = self._make_request('GET', f'policies/bindings/?target={target_uuid}&group={group_uuid}')
            if bindings['results']:
                binding_uuid = bindings['results'][0]['pk']
                print(f"✓ Found existing group binding with UUID: {binding_uuid}")
                return binding_uuid
        except Exception as e:
            print(f"Error checking for existing binding: {e}")

        # Create new binding if not found
        data = {
            "policy": None,
            "group": group_uuid,
            "user": None,
            "target": target_uuid,
            "negate": False,
            "enabled": True,
            "order": str(order),
            "timeout": "30",
            "failure_result": False
        }

        print(f"Binding group to target")
        result = self._make_request('POST', 'policies/bindings/', data)
        binding_uuid = result['pk']
        print(f"✓ Group binding created with UUID: {binding_uuid}")
        return binding_uuid

    def assign_application_to_outpost(self, outpost_uuid: str, application_slug: str):
        """
        Assign application to an outpost

        Args:
            outpost_uuid: UUID of the outpost
            application_slug: UUID of the application
        """
        # First, get the current outpost configuration
        print(f"Getting outpost configuration")
        outpost_data = self._make_request('GET', f'outposts/instances/{outpost_uuid}/')

        # Add the application to the outpost's providers
        current_providers = outpost_data.get('providers', [])

        # Get the provider ID from the application
        app_data = self._make_request('GET', f'core/applications/{application_slug}/')
        provider_id = app_data['provider']

        if provider_id not in current_providers:
            current_providers.append(provider_id)

            # Update the outpost
            update_data = {
                "name": outpost_data['name'],
                "type": outpost_data['type'],
                "providers": current_providers,
                "config": outpost_data['config']
            }

            print(f"Assigning application to outpost")
            self._make_request('PUT', f'outposts/instances/{outpost_uuid}/', update_data)
            print(f"✓ Application assigned to outpost")
        else:
            print(f"✓ Application already assigned to outpost")

    def get_outposts(self) -> Dict[str, Any]:
        """Get list of available outposts"""
        return self._make_request('GET', 'outposts/instances/')

    def setup_complete_configuration(self,
                                     group_name: str,
                                     provider_name: str,
                                     app_name: str,
                                     app_slug: str,
                                     external_host: str,
                                     outpost_uuid: str = None,
                                     internal_host: str = None) -> Dict[str, str]:
        """
        Complete setup: create group, provider, application, policy, and bindings

        Args:
            group_name: Name of the access group
            provider_name: Name of the proxy provider
            app_name: Name of the application
            app_slug: URL slug for the application
            external_host: External URL for the proxy
            outpost_uuid: UUID of outpost to assign to (optional)
            internal_host: Internal URL to proxy to

        Returns:
            Dictionary with created resource UUIDs/IDs
        """
        print("=== Starting Authentik Configuration ===\n")

        # Create group
        group_uuid = self.get_or_create_group(group_name)

        # Create proxy provider
        provider_id = self.get_or_create_proxy_provider(
            provider_name, external_host, internal_host
        )

        # Create application
        app_uuid = self.get_or_create_application(app_name, app_slug, provider_id)

        # Create group membership policy

        # Bind policy to application
        binding_uuid = self.get_or_create_group_binding(app_uuid, group_uuid)

        # Assign to outpost if specified
        outposts = self.get_outposts()
        if len(outposts['results']) == 1:
            outpost_uuid = outposts['results'][0]['pk']
            self.assign_application_to_outpost(outpost_uuid, app_slug)

        print("\n=== Configuration Complete ===")

        return {
            "group_uuid": group_uuid,
            "provider_id": provider_id,
            "app_uuid": app_uuid,
            "binding_uuid": binding_uuid
        }


# Example usage
if __name__ == "__main__":
    # Configuration
    AUTHENTIK_URL = "https://auth.example.com"  # Replace with your Authentik URL
    API_TOKEN = "your-api-token-here"  # Replace with your API token

    # Initialize configurator
    auth_config = AuthentikConfigurator(AUTHENTIK_URL, API_TOKEN)

    # Example configuration
    config_params = {
        "group_name": "MyApp Users",
        "provider_name": "MyApp Proxy Provider",
        "app_name": "My Application",
        "app_slug": "myapp",
        "external_host": "https://myapp.example.com",
        "internal_host": "http://localhost:8080",
        # "outpost_uuid": "your-outpost-uuid-here"  # Uncomment and set if needed
    }

    try:
        # Run complete setup
        results = auth_config.setup_complete_configuration(**config_params)

        print("\n=== Created Resources ===")
        for resource_type, resource_id in results.items():
            print(f"{resource_type}: {resource_id}")

        print(
            f"\n✓ Setup complete! Users must be members of '{config_params['group_name']}' to access the application.")

    except Exception as e:
        print(f"\n❌ Configuration failed: {e}")