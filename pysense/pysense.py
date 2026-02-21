import argparse, sys, yaml, getpass
import os
from pathlib import Path
from pysense.client import Client
from pprint import pprint


def load_cfg(path: Path) -> dict:
    if not path.exists(): return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def pick(key, default, env_map, cli_val):
    return cli_val if cli_val is not None else os.getenv(env_map, default)


def save_cfg(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def cmd_config(args):
    cfg_path = Path(args.config)
    cfg = load_cfg(cfg_path)

    if cfg:
        print("Current config:")
        pprint(cfg)
        if input("Update values? [y/N] ").lower() != "y":
            return

    def ask(key, default=None, secret=False):
        prompt = f"{key} [{default or ''}]: "
        val = (getpass.getpass if secret else input)(prompt).strip()
        return val or default

    new_cfg = {
        "api_key":        ask("API key",         cfg.get("api_key"),       secret=True),
        "api_secret":     ask("API secret",      cfg.get("api_secret"),    secret=True),
        "opnsense_url":   ask("OPNsense URL",    cfg.get("opnsense_url")),
        "timeout":        int(ask("Timeout",     cfg.get("timeout", 10))),
        "verify_cert":    ask("Verify cert",     cfg.get("verify_cert", "root-ca.pem")),
        "authentik_url":  ask("Authentik URL",   cfg.get("authentik_url")),
        "authentik_host": ask("Authentik Host",  cfg.get("authentik_host")),
        "authentik_ip":   ask("Authentik IP",    cfg.get("authentik_ip")),
        "authentik_port": ask("Authentik Port",  cfg.get("authentik_port")),
        "authentik_token":ask("Authentik Token", cfg.get("authentik_token"), secret=True),
        # "group_name":    ask("Group Name",    cfg.get("group_name")),
        # "provider_name": ask("Provider Name", cfg.get("provider_name")),
        # "app_name":      ask("App Name",      cfg.get("app_name")),
        # "app_slug":      ask("App Slug",      cfg.get("app_slug")),
        # "external_host": ask("External Host", cfg.get("external_host")),
    }
    save_cfg(cfg_path, new_cfg)
    print(f"Saved → {cfg_path}")


def main():
    """
    CLI wrapper for haproxy_simple_proxy()

    Priority config.yml  <  env vars  <  CLI flags
    """
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument('--config', default='config.yml')
    parent.add_argument('--api-key')
    parent.add_argument('--api-secret')
    parent.add_argument('--opnsense-url')
    parent.add_argument('--timeout', type=int, default=10)
    parent.add_argument('--verify-cert', default='root-ca.pem')
    parent.add_argument('--debug', type=bool, default=False)

    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("haproxy", parents=[parent], help="create a simple HAProxy rule")
    h.add_argument('--domain', required=True)
    h.add_argument('--ip', required=True)
    h.add_argument('--port', type=int, required=True)
    h.add_argument('--frontend', required=True)
    h.add_argument('--ssl-provider')
    h.add_argument('--domain-aliases', nargs='*')
    h.add_argument('--sso')
    h.add_argument('--username')
    h.add_argument('--password')
    # Authentik options
    h.add_argument('--authentik-url')
    h.add_argument('--authentik-host')
    h.add_argument('--authentik-ip')
    h.add_argument('--authentik-port')
    h.add_argument('--authentik-token')
    h.add_argument('--group-name')
    h.add_argument('--provider-name')
    h.add_argument('--app-name')
    h.add_argument('--app-slug')
    h.add_argument('--external-host')

    s = sub.add_parser("sso", parents=[parent], help="enable disable sso on haproxy")
    s.add_argument('--domain', required=True)
    s.add_argument('--enable', action='store_true')
    s.add_argument('--disable', action='store_true')
    c = sub.add_parser("config", parents=[parent], help="interactive config editor")

    args = p.parse_args()
    cfg = load_cfg(Path(args.config))

    api_key = pick('api_key', cfg.get('api_key'), 'API_KEY', args.api_key)
    api_secret = pick('api_secret', cfg.get('api_secret'), 'API_SECRET', args.api_secret)
    opnsense_url = pick('opnsense_url', cfg.get('opnsense_url'), 'OPNSENSE_URL', args.opnsense_url)
    timeout = pick('timeout', cfg.get('timeout', 10), 'OPNS_TIMEOUT', args.timeout)
    verify_cert = pick('verify_cert', cfg.get('verify_cert', 'root-ca.pem'), 'OPNS_VERIFY_CERT', args.verify_cert)

    if args.cmd == "config":
        cmd_config(args)
        return

    if not all([api_key, api_secret, opnsense_url]):
        sys.exit('api-key, api-secret and opnsense-url must be supplied (cfg/env/cli).')

    client = Client(api_key, api_secret, opnsense_url, timeout=int(timeout), verify_cert=verify_cert)
    client.debug = args.debug
    action = None
    if args.cmd == "haproxy":
        sso_result = None
        if args.sso:
            # Resolve Authentik parameters
            auth_url = pick('authentik_url', cfg.get('authentik_url'), 'AUTHENTIK_URL', args.authentik_url)
            auth_host = pick('authentik_host', cfg.get('authentik_host'), 'AUTHENTIK_HOST', args.authentik_host)
            auth_ip = pick('authentik_ip', cfg.get('authentik_ip'), 'AUTHENTIK_IP', args.authentik_ip)
            auth_port = pick('authentik_port', cfg.get('authentik_port'), 'AUTHENTIK_PORT', args.authentik_port)
            auth_token = pick('authentik_token', cfg.get('authentik_token'), 'AUTHENTIK_TOKEN', args.authentik_token)
            group_name = pick('group_name', cfg.get('group_name'), 'AUTHENTIK_GROUP', args.group_name)
            provider_name = pick('provider_name', cfg.get('provider_name'), 'AUTHENTIK_PROVIDER', args.provider_name)
            app_name = pick('app_name', cfg.get('app_name'), 'AUTHENTIK_APP_NAME', args.app_name)
            app_slug = pick('app_slug', cfg.get('app_slug'), 'AUTHENTIK_APP_SLUG', args.app_slug)
            external_host = pick('external_host', cfg.get('external_host'), 'AUTHENTIK_EXTERNAL_HOST', args.external_host)

            if not all([auth_url, auth_token, group_name, provider_name, app_name, app_slug, external_host]):
                sys.exit("Missing required Authentik parameters (cfg/env/cli).")

            from pysense.authentik import AuthentikConfigurator
            auth_config = AuthentikConfigurator(auth_url, auth_token)
            config_params = {
                "group_name": group_name,
                "provider_name": provider_name,
                "app_name": app_name,
                "app_slug": app_slug,
                "external_host": external_host,
            }
            try:
                results = auth_config.setup_complete_configuration(**config_params)
                print("\n=== Created Authentik Resources ===")
                for k, v in results.items():
                    print(f"{k}: {v}")
                print(f"\n✓ Setup complete! Group: '{group_name}'")
            except Exception as e:
                print(f"\n❌ Authentik configuration failed: {e}")
                sys.exit(1)

            client.authentik_lua_check()
            action = client.authentik_acl_check(args.frontend, auth_host,auth_ip, auth_port)


        acl_uuid_primary = client.haproxy_simple_proxy(
            domain=args.domain,
            ip=args.ip,
            port=args.port,
            frontend=args.frontend,
            ssl_provider=args.ssl_provider,
            domain_aliases=args.domain_aliases or [],
            sso=action,
            username=args.username,
            password=args.password
        )

        if args.sso:
            client.enable_sso(args.domain)

    if args.cmd == "sso":
        if args.enable:
            print('enabling sso for {domain}'.format(domain=args.domain))
            client.enable_sso(args.domain)
            client.restart_if_possible()
        elif args.disable:
            print('disable sso for {domain}'.format(domain=args.domain))
            client.disable_sso(args.domain)
            client.restart_if_possible()
        else:
            acl_uuid = client.acl_sso()
            acl = client.haproxy_settings_getAcl(acl_uuid)
            print(acl.acl.hdr)


if __name__ == '__main__':
    main()
