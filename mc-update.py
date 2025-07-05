#!/usr/bin/env python3

import time
import json
import sys
import os
import urllib.request

# Configuration
USE_LATEST_RELEASE = True # True = use latest release, False = use snapshot
ARGS = sys.argv[1:]
if "release" in ARGS:
    USE_LATEST_RELEASE = True
elif "snapshot" in ARGS:
    USE_LATEST_RELEASE = False
INTERNET_RETRY_DELAY = 20  # Delay in seconds for retrying internet connection
MMC_CONFIG_FILE = "mmc-pack.json"  # Name of the MultiMC / PrisimLauncher configuration file
MC_VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json" # The offical minecraft versions json

# Constants
SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
MMC_CONFIG_PATH = os.path.join(SCRIPT_DIR, MMC_CONFIG_FILE)

def download_version_manifest(url, retries):
    """Download the Minecraft version manifest JSON."""
    retries = max(retries, 1)  # Ensure at least one retry attempt

    while retries > 0:
        try:
            response = urllib.request.urlopen(url)
            return json.loads(response.read())
        except Exception:
            retries -= 1
            if retries == 0:
                print("No Internet Found. Exiting...")
                time.sleep(2)
                sys.exit(1)
            if (retries % 10) == 9:
                print(f"\nInternet connection missing. Retrying {retries + 1} more times (every second).")
            time.sleep(1)
        else:
            print("\nInternet connection restored. Continuing...\n")
            retries = 0

def load_mmc_config(config_path):
    """Load the MultiMC / PrismLauncher configuration file."""
    if not os.path.exists(config_path):
        print("MultiMC / PrismLauncher configuration file not found. Please place this script in the instance root directory. Exiting...")
        time.sleep(2)
        sys.exit(1)

    with open(config_path, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("MultiMC / PrismLauncher configuration file is not a valid JSON. Please use another instance. Exiting...")
            time.sleep(2)
            sys.exit(1)

def save_mmc_config(config_path, mmc_json):
    with open(config_path, 'w') as file:
        json.dump(mmc_json, file, sort_keys=True, indent=4)

def update_mmc_config(json_data, new_version):
    """Update the MultiMC / PrismLauncher configuration with the new version."""
    components = mmc_json.get("components", [])

    # Find the component with "uid": "net.minecraft"
    mc_component = next((c for c in components if c.get("uid") == "net.minecraft"), None)

    if not mc_component or "version" not in mc_component:
        print("Could not find the Minecraft component in mmc-pack.json. Exiting...")
        time.sleep(2)
        sys.exit(1)

    current_version = mc_component["version"]

    if current_version == new_version:
        print(f"MultiMC / PrismLauncher is already on the latest version: {new_version}")
        time.sleep(2)
        sys.exit(0)
    else:
        mc_component["version"] = new_version
        print(f"Installed Version = {current_version}\nUpdated To Version = {new_version}")

    return mmc_json

def main():
    print("Downloading and reading Minecraft version manifest...")
    version_manifest = download_version_manifest(MC_VERSION_MANIFEST_URL, retries=INTERNET_RETRY_DELAY)

    print("Extracting Minecraft versions...")
    latest_release = version_manifest["latest"]["release"]
    latest_snapshot = version_manifest["latest"]["snapshot"]
    selected_version = latest_release if USE_LATEST_RELEASE else latest_snapshot

    print(f"\nUsing newest {'release' if USE_LATEST_RELEASE else 'snapshot'}: {selected_version}")

    print("Loading MultiMC / PrismLauncher configuration...")
    mmc_json = load_mmc_config(MMC_CONFIG_PATH)

    print("Updating configuration...")
    mmc_json_data = update_mmc_config(json_data=mmc_json, new_version=selected_version)

    if mmc_json != mmc_json_data:
        print("Saving configuration...")
        save_mmc_config(MMC_CONFIG_PATH, mmc_json_data)
    else:
        print("Configuration already on newest version...")

if __name__ == "__main__":
    main()
