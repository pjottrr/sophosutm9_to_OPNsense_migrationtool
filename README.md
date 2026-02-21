# Sophos UTM 9 to OPNsense Migration Tools

This repository contains a set of Python scripts to assist in migrating a Sophos UTM 9 configuration to OPNsense. The tools parse the Sophos XML configuration export and import objects (Aliases, Firewall Rules, NAT, etc.) into OPNsense via the API. When this script was executed in our environment sophos utm was the latest version, and opnsense was on version 26.1

## Prerequisites

*   **Python 3.10+**
*   **OPNsense** instance (reachable via network)
*   **Sophos UTM 9** configuration backup (`.xml` format)

### Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
# Or manually:
pip install lxml requests pydantic pyyaml selenium webdriver-manager
```

## Configuration

Before running the scripts, open them in a text editor and fill in your OPNsense credentials at the top of the file.

*   **`opnsense_alias_import.py`** & **`opnsense_firewall_import.py`**:
    *   Set `OPNSENSE_URL`, `OPNSENSE_KEY`, and `OPNSENSE_SECRET`.
*   **`opnsense_interface_setup.py`**:
    *   Set `OPNSENSE_HOST`, `OPNSENSE_PORT`, `OPNSENSE_USER`, and `OPNSENSE_PASS`.

> **Note:** To generate an API Key in OPNsense, go to **System > Access > Users**, edit your user, and click the **+** button under "API keys".

## Migration Workflow

Follow these steps in order to perform the migration.

### 1. Parse Sophos Configuration

First, export your configuration from Sophos UTM 9 as an unencrypted XML file (e.g., `webadmin.xml`).

Run the parser to convert the XML into intermediate JSON files:

```bash
python sophos_parser.py webadmin.xml output/
```

This will populate the `output/` directory with JSON files (`hosts.json`, `services.json`, `firewall_rules.json`, etc.).

### 2. Import Aliases (Hosts, Networks, Services)

Import all definitions into OPNsense aliases. This script handles Hosts, Networks, Ports, and Groups.

```bash
python opnsense_alias_import.py
```

*   **Note:** This script will attempt to delete existing non-system aliases to ensure a clean import.

### 3. Setup Interfaces (Optional)

Since the OPNsense API does not fully support creating interface assignments, this script uses Selenium (browser automation) to create them.

*   Edit `opnsense_interface_setup.py` to define `INTERFACES_TO_CREATE` list with your specific interface mappings.
*   Ensure you have Chrome installed.

```bash
python opnsense_interface_setup.py
```

### 4. Import Firewall & NAT Rules

This script imports Firewall rules, DNAT (Port Forwarding), and SNAT (Outbound NAT) rules.

```bash
python opnsense_firewall_import.py
```

*   The script will check for an `interface_mapping.json`. If it doesn't exist or if new interfaces are found, it will generate a template.
*   **Action:** Run the script once, edit the generated `mapping.json` to map Sophos interface names (e.g., "Internal") to OPNsense interfaces (e.g., "lan"), and run the script again.

### 5. Generate HAProxy Configuration (WAF)

If you used the Web Application Firewall (WAF) in Sophos, this script generates a configuration structure for HAProxy.

```bash
python generate_haproxy.py output/
```

This outputs a JSON file and a reference `.cfg` file. Note that importing this into OPNsense HAProxy plugin usually requires manual steps or a specific import logic depending on your setup, as the OPNsense HAProxy API is complex.

## OPNsense API Library

This tool relies on a library (currently named `pysense` in this repo) to interact with the OPNsense API. This library is being renamed to **opnsense_api** and will be maintained in a separate repository, as it provides broader functionality for OPNsense automation (managing HAProxy, creating firewall rules, etc.).

*   **Link**: https://github.com/park0/opnsense_api

## Authors & Credits

*   **Park0** (Main Developer) - Creator of the Sophos migration tool and the `opnsense_api` library.
*   **Pjottrr** - Contributor.
*   **AI Contributors** - Portions of this project were developed with the assistance of **Google Gemini** and **Anthropic Claude**.

## Disclaimer

Always backup your OPNsense configuration before running these scripts. Review the generated rules after import.
