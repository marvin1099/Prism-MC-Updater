#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import time
import threading
import shutil
import urllib.request
from pathlib import Path


INTERNET_RETRY_DELAY = 20
MC_VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
MMC_CONFIG_FILENAME = "mmc-pack.json"

def print_help():
    print(f"""A Minecraft Auto-Updater Wrapper Script for PrismLauncher Instances

Usage (in PrismLauncher → Right Click Instance → Edit → Settings → Custom Commands → Wrapper Command):
    \"{__file__}\" [options]

Options:
    --release            Use the latest release version (default)
    --snapshot           Use the latest snapshot version
    --subprocess_log     Enable log for the spawed subprocess.
                         The file will be at INSTANCE-FOLDER/wrapper_subprocess.log

    --prism_path PATH    Path to the PrismLauncher / MultiMC executable
                         If omitted, prismlauncher / multimc must be available in PATH.

    --instance_dir PATH  Use this as the instance directory instead of the current one
                         This must be the instance root directory.

    --end_up_wrapper     This is optional and sets the end of the wrapper arguments.
                         This is usefull for something like optirun.
                         By adding --end_wrapper at the end you can then add optirun afterwards

    --help               Show this help message

Example (most basic but should work):
    \"{__file__}\"

Example with prism_path and snapshot:
    \"{__file__}\" --prism_path \"/usr/bin/prismlauncher\" --snapshot

Example with optirun and release specified:
    \"{__file__}\" --release --end_up_wrapper optirun

""")
    sys.exit(0)

def split_wrapper_and_game_args(argv):
    java_names = [
        "java", "java.exe",
        "javaw", "javaw.exe",
        "openjdk", "openjdk.exe",
        "temurin", "temurin.exe",     # e.g. Eclipse Adoptium
        "zulu", "zulu.exe",           # e.g. Azul Zulu
        "graalvm", "graalvm.exe"      # advanced users
    ]

    if "--end_up_wrapper" in argv:
        end_index = sys.argv.index("--end_up_wrapper")
        wrapper_args = sys.argv[1:end_index]
        prism_args = sys.argv[end_index + 1:]
        return wrapper_args, prism_args
    else:
        # Find first argument that looks like Java command
        for i in range(len(argv)-1, -1, -1):
            arg = Path(argv[i])
            if arg.name.lower() in java_names:
                return argv[1:i], argv[i:]
        return argv[1:], []  # fallback if no Java found

def parse_args():
    if "--help" in sys.argv:
        print_help()

    wrapper_args, prism_args = split_wrapper_and_game_args(sys.argv)

    use_release = "--snapshot" not in wrapper_args or "--release" in wrapper_args

    # Known Prism/MultiMC launcher executables (Linux, Windows, macOS)
    prism_names = [
        "prismlauncher",              # Linux / macOS CLI
        "prism-launcher",
        "prismlauncher.exe",          # Windows
        "prism-launcher.exe",
        "MultiMC",                    # Old MultiMC binary
        "MultiMC.exe",
        "multimc",                    # lowercase variants
        "multimc.exe"
    ]

    # If --prism_path is provided, try to resolve it first
    if "--prism_path" in wrapper_args:
        idx = wrapper_args.index("--prism_path")
        try:
            given_path = wrapper_args[idx + 1]
        except IndexError as e:
            print(f"--prism_path requires a path")
            sys.exit(1)
        except Exception as e:
            print(f"Exiting as --prism_path has unknown error: {e}")
            sys.exit(1)

        # Try full path first
        if Path(given_path).is_file() and os.access(given_path, os.X_OK):
            return Path(given_path).resolve()
        else:
            resolved = Path(shutil.which(given_path)).resolve()
            if resolved:
                return resolved
            else:
                print(f"The given path '{given_path}' could not be resolved.")
                sys.exit(1)

    # Otherwise, search known names in PATH
    for name in prism_names:
        resolved = Path(shutil.which(name)).resolve()
        if resolved:
            prism_path = resolved
            break

    if not prism_path:
        print("App prismlauncher / multimc could not be found.")
        print("The argument --prism_path will need to be set to the full path of prismlauncher / multimc.")
        print("Eg. '\"{__file__}\" --prism_path \"/usr/bin/prismlauncher\" --snapshot'.")
        sys.exit(1)

    working_dir = Path(os.getcwd())

    if "--instance_dir" in wrapper_args:
        idx = wrapper_args.index("--instance_dir")
        try:
            working_dir = Path(wrapper_args[idx + 1]).resolve()
            if not working_dir.is_dir():
                raise TypeError("Not a dir valid path")
        except IndexError:
            print("--instance_dir requires a path.")
            sys.exit(1)
        except TypeError:
            print("--instance_dir requires a valid dirrectory path.")
            sys.exit(1)
        except Exception as e:
            print(f"Exiting as --instance_dir has unknown error: {e}")
            sys.exit(1)

    subprocess_log = "--subprocess_log" in wrapper_args

    if working_dir.name == ".minecraft" and not (working_dir / MMC_CONFIG_FILENAME).is_file():
        working_dir = working_dir.parent

    return use_release, prism_path, working_dir, prism_args, subprocess_log

def download_version_manifest(url, retries):
    retries = max(retries, 1)
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
                print(f"\nInternet missing. Retrying {retries + 1} more times...")
            time.sleep(1)

def load_mmc_config(path):
    if not path.is_file():
        print(f"Missing config: {str(path)}")
        sys.exit(1)
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in mmc-pack.json.")
            sys.exit(1)

def save_mmc_config(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

def get_mc_component(mmc_json):
    return next((c for c in mmc_json.get("components", []) if c.get("uid") == "net.minecraft"), None)

def needs_update(instance_path, mcc_config, use_release):
    config_path = Path(instance_path, mcc_config)
    mmc_json = load_mmc_config(config_path)

    mc_component = get_mc_component(mmc_json)
    if not mc_component or "version" not in mc_component:
        print("Could not find Minecraft component in mmc-pack.json.")
        sys.exit(1)

    current_version = mc_component["version"]
    manifest = download_version_manifest(MC_VERSION_MANIFEST_URL, retries=INTERNET_RETRY_DELAY)
    target_version = manifest["latest"]["release"] if use_release else manifest["latest"]["snapshot"]

    if current_version != target_version:
        print(f"Update needed: {current_version} → {target_version}")
        return True, mmc_json, config_path, target_version
    else:
        print(f"Up-to-date: {current_version}")
        return False, None, None, None

def detach_and_relaunch(prism_path, instance_id, mmc_json, config_path, new_version, subprocess_log, timeout=5):
    print(f"Relaunching PrismLauncher with updated version in max {timeout}s...")

    # Serialize mmc_json and new_version to pass to the detached subprocess
    launch_script = f"""
import time, json, subprocess, traceback, os

ENABLE_LOG = {subprocess_log}
LOG_PATH = {repr(str(config_path.parent / "wrapper_subprocess.log"))}
CONFIG_PATH = {repr(str(config_path))}
NEW_VERSION = {repr(new_version)}
PRISM_CMD = { [str(prism_path), "--launch", instance_id]!r }
TIMEOUT = {timeout}

if ENABLE_LOG and os.path.isfile(LOG_PATH):
    os.remove(LOG_PATH)

def log(msg):
    if ENABLE_LOG:
        with open(LOG_PATH, 'a') as f:
            f.write(msg + '\\n')
            f.flush()
    else:
        print(msg)

def wait_for_touch(path, old_mtime, timeout=TIMEOUT, interval=0.1):
    start = time.time()
    while time.time() - start < timeout:
        try:
            new_mtime = os.path.getmtime(path)
            if new_mtime > old_mtime:
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False

log('Watching for mmc-pack.json change...')
try:
    initial_mtime = os.path.getmtime(CONFIG_PATH)
except Exception as e:
    log('Failed to stat config: ' + str(e))
    log(traceback.format_exc())
    initial_mtime = time.time()

touched = wait_for_touch(CONFIG_PATH, initial_mtime)

if not touched:
    log('Timeout waiting for Prism to update config. Proceeding anyway.')
else:
    log('Detected config file change.')

try:
    log('Rewriting version in config...')
    with open(CONFIG_PATH, 'r+') as f:
        data = json.load(f)
        for comp in data.get("components", []):
            if comp.get("uid") == "net.minecraft":
                comp["version"] = NEW_VERSION
                break
        f.seek(0)
        json.dump(data, f, indent=4, sort_keys=True)
        f.truncate()
except Exception as e:
    log('Failed to patch config: ' + str(e))
    log(traceback.format_exc())
    raise

try:
    log('Launching Prism...')
    subprocess.run(PRISM_CMD, check=True)
    log('Prism launched successfully.')
except Exception as e:
    log('Failed to launch Prism: ' + str(e))
    log(traceback.format_exc())

log('Done.')
"""

    python_exe = sys.executable  # current Python interpreter

    # Fully detached, silent subprocess
    subprocess.Popen(
        [python_exe, "-c", launch_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True  # Important: prevents signal propagation
    )

    time.sleep(0.1)

    print()
    sys.exit(0)


def main():
    print()
    use_release, prism_path, instance_path, prism_args, subprocess_log = parse_args()

    instance_id = os.path.basename(instance_path)

    print(f"Instance ID: {instance_id}")
    print(f"Checking for {'release' if use_release else 'snapshot'} updates...")

    update_needed, mmc_json, config_path, new_version = needs_update(instance_path, MMC_CONFIG_FILENAME, use_release)

    if update_needed:
        if not prism_args:
            print("Manual launch detected. Applying update and exiting...")
            mc_component = get_mc_component(mmc_json)
            mc_component["version"] = new_version
            save_mmc_config(config_path, mmc_json)
            print(f"Updated to {new_version}.")
            print()
            sys.exit(0)
        else:
            detach_and_relaunch(prism_path, instance_id, mmc_json, config_path, new_version, subprocess_log)
    else:
        if prism_args:
            print(f"Launching game...")
            subprocess.run(prism_args)
        else:
            print("Manual launch detected. Exiting...")
        print()

if __name__ == "__main__":
    main()
