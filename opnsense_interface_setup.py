#!/usr/bin/env python3
"""
OPNsense Interface Setup via Web UI Automation

Creates interfaces in OPNsense using Selenium browser automation.
This is needed because the OPNsense API does not support interface creation.

Requirements:
    pip install selenium webdriver-manager

Usage:
    python opnsense_interface_setup.py
"""

import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# OPNsense Web UI credentials
OPNSENSE_HOST = "192.168.1.1"
OPNSENSE_PORT = "443"
OPNSENSE_USER = "root"
OPNSENSE_PASS = "your_password_here"

# Interface configurations to create
# Each entry: (description, network_port, ip_config)
# network_port options depend on your hardware (vtnet0, vtnet1, em0, em1, etc.)
INTERFACES_TO_CREATE = [
    # Example configurations - adjust to match your Sophos interfaces
    # ('DMZ', 'vtnet2', {'type': 'static', 'ip': '192.168.10.1', 'subnet': '24'}),
    # ('Internal', 'vtnet3', {'type': 'dhcp'}),
]


def check_selenium():
    """Check if Selenium is available."""
    if not SELENIUM_AVAILABLE:
        print("ERROR: Selenium is not installed.")
        print("Install it with: pip install selenium webdriver-manager")
        return False
    return True


def create_driver():
    """Create a Chrome WebDriver with appropriate options."""
    options = Options()
    options.add_argument('--headless')  # Run without GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')  # Accept self-signed certs
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        # Fallback to system Chrome driver
        driver = webdriver.Chrome(options=options)

    return driver


def login_to_opnsense(driver):
    """Log in to OPNsense web interface."""
    url = f"https://{OPNSENSE_HOST}:{OPNSENSE_PORT}/"
    print(f"Navigating to {url}...")
    driver.get(url)

    # Wait for login form
    wait = WebDriverWait(driver, 10)

    try:
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "usernamefld")))
        password_field = driver.find_element(By.NAME, "passwordfld")

        username_field.send_keys(OPNSENSE_USER)
        password_field.send_keys(OPNSENSE_PASS)

        # Find and click login button
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        # Wait for dashboard to load
        time.sleep(3)

        if "Dashboard" in driver.page_source or "dashboard" in driver.current_url.lower():
            print("  Login successful!")
            return True
        else:
            print("  Login may have failed - checking...")
            return "login" not in driver.current_url.lower()

    except Exception as e:
        print(f"  Login error: {e}")
        return False


def get_existing_interfaces(driver):
    """Get list of existing interface assignments."""
    url = f"https://{OPNSENSE_HOST}:{OPNSENSE_PORT}/interfaces_assign.php"
    driver.get(url)
    time.sleep(2)

    interfaces = []
    try:
        # Find interface assignment table
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                iface_name = cells[0].text.strip()
                if iface_name and iface_name not in ['', 'Interface', 'Add']:
                    interfaces.append(iface_name)
    except Exception as e:
        print(f"  Error getting interfaces: {e}")

    return interfaces


def add_interface_assignment(driver, description):
    """Add a new interface assignment."""
    url = f"https://{OPNSENSE_HOST}:{OPNSENSE_PORT}/interfaces_assign.php"
    driver.get(url)
    time.sleep(2)

    try:
        # Find the "Add" button/link
        add_link = driver.find_element(By.CSS_SELECTOR, "a[href*='act=add']")
        add_link.click()
        time.sleep(2)

        print(f"  Added new interface assignment")
        return True

    except Exception as e:
        print(f"  Error adding interface: {e}")
        return False


def configure_interface(driver, interface_id, config):
    """Configure an interface with IP settings."""
    url = f"https://{OPNSENSE_HOST}:{OPNSENSE_PORT}/interfaces.php?if={interface_id}"
    driver.get(url)
    time.sleep(2)

    try:
        # Enable the interface
        enable_checkbox = driver.find_element(By.ID, "enable")
        if not enable_checkbox.is_selected():
            enable_checkbox.click()

        # Set description if provided
        if 'description' in config:
            desc_field = driver.find_element(By.ID, "descr")
            desc_field.clear()
            desc_field.send_keys(config['description'])

        # Set IP configuration type
        if config.get('type') == 'static':
            type_select = Select(driver.find_element(By.ID, "type"))
            type_select.select_by_value("staticv4")
            time.sleep(1)

            # Set IP address
            if 'ip' in config:
                ip_field = driver.find_element(By.ID, "ipaddr")
                ip_field.clear()
                ip_field.send_keys(config['ip'])

            # Set subnet mask
            if 'subnet' in config:
                subnet_select = Select(driver.find_element(By.ID, "subnet"))
                subnet_select.select_by_value(str(config['subnet']))

        elif config.get('type') == 'dhcp':
            type_select = Select(driver.find_element(By.ID, "type"))
            type_select.select_by_value("dhcp")

        # Save changes
        save_button = driver.find_element(By.ID, "submit")
        save_button.click()
        time.sleep(3)

        print(f"  Interface {interface_id} configured successfully")
        return True

    except Exception as e:
        print(f"  Error configuring interface: {e}")
        return False


def apply_changes(driver):
    """Apply pending interface changes."""
    try:
        # Look for "Apply changes" button
        apply_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary[type='submit']")
        if "Apply" in apply_button.text:
            apply_button.click()
            time.sleep(5)
            print("  Changes applied!")
            return True
    except Exception:
        pass
    return False


def main():
    print("=" * 60)
    print("OPNsense Interface Setup (Web UI Automation)")
    print("=" * 60)

    if not check_selenium():
        return

    if not OPNSENSE_PASS:
        print("\nERROR: Please set OPNSENSE_PASS in this script.")
        print("Edit opnsense_interface_setup.py and set the password.")
        return

    if not INTERFACES_TO_CREATE:
        print("\nNo interfaces configured to create.")
        print("Edit INTERFACES_TO_CREATE in this script to add interface configurations.")
        print("\nExample:")
        print("INTERFACES_TO_CREATE = [")
        print("    ('DMZ', 'vtnet2', {'type': 'static', 'ip': '192.168.10.1', 'subnet': '24'}),")
        print("    ('Guest', 'vtnet3', {'type': 'dhcp'}),")
        print("]")
        return

    print("\nStarting browser automation...")
    driver = create_driver()

    try:
        # Login
        print("\n=== Logging in to OPNsense ===")
        if not login_to_opnsense(driver):
            print("ERROR: Failed to log in to OPNsense")
            return

        # Get existing interfaces
        print("\n=== Checking existing interfaces ===")
        existing = get_existing_interfaces(driver)
        print(f"Found {len(existing)} existing interfaces: {', '.join(existing)}")

        # Create new interfaces
        print("\n=== Creating new interfaces ===")
        for desc, port, config in INTERFACES_TO_CREATE:
            print(f"\nCreating interface: {desc}")
            if add_interface_assignment(driver, desc):
                config['description'] = desc
                # The new interface will be optX where X is the next number
                # This is simplified - real implementation needs more logic
                print(f"  Note: Configure this interface manually in OPNsense UI")

        # Apply changes
        print("\n=== Applying changes ===")
        apply_changes(driver)

        print("\n" + "=" * 60)
        print("SETUP COMPLETE")
        print("=" * 60)
        print("\nNote: Due to complexity of OPNsense interface setup,")
        print("you may need to complete configuration manually in the web UI.")
        print(f"\nWeb UI: https://{OPNSENSE_HOST}:{OPNSENSE_PORT}/interfaces_assign.php")

    finally:
        driver.quit()
        print("\nBrowser closed.")


if __name__ == "__main__":
    main()
