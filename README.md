# Prism-MC-Updater

## Description

A powerful yet simple Minecraft version auto-updater for PrismLauncher and MultiMC instances.

It ensures your selected instance always launches the **latest release or snapshot** version of Minecraft — without needing to manually adjust the configuration every time Mojang pushes an update.

## Features

* Supports both **release** and **snapshot** Minecraft versions
* Fully compatible with **PrismLauncher wrapper commands**
* Can still be used as a **pre-launch command** (works in MultiMC, but may not be effective in newer PrismLauncher versions due to config overwrite behavior)
* Detects whether an update is needed before patching
* Can auto-relaunch the launcher with updated version settings if needed

## Installation

1. Download the latest script from:

   * [Codeberg Releases](https://codeberg.org/marvin1099/MultiMC-LatestVer/releases)
   * [GitHub Releases](https://github.com/marvin1099/MultiMC-LatestVer/releases)

2. Make the script executable (Linux/macOS):

   ```bash
   chmod +x mc-update.py
   ```

## Requirements

* Python 3.x installed
* MultiMC or PrismLauncher installed

---

## Usage

### A) PrismLauncher Wrapper Mode (Recommended for Prism)

1. Open **PrismLauncher**.
2. Right-click your instance → **Folder**
3. Place the script inside the opened instance directory
4. Right-click your instance → **Edit** → **Settings** tab.
5. Under **Custom Commands**, paste the following into the **Wrapper Command** field:

#### Basic usage (default: latest release)

* **Linux/macOS:**

```bash
python3 "$INST_DIR/mc-update.py"
```

* **Windows:**

```cmd
python "%INST_DIR%\\mc-update.py"
```

Most of these commands are defined for **Linux/macOS**  
If you are on **Windows** you will need to change them to fit the format above.

#### With snapshot version:

```bash
python3 "$INST_DIR/mc-update.py" --snapshot
```

#### With custom Prism path and subprocess logging:

```bash
python3 "$INST_DIR/mc-update.py" --snapshot --prism_path "/usr/bin/prismlauncher" --subprocess_log
```

#### With `optirun` or other GPU wrappers:

```bash
python3 "$INST_DIR/mc-update.py" --end_up_wrapper optirun
```

> All wrapper arguments go before `--end_up_wrapper`. Anything after that is treated as the command to run Minecraft (usually inserted automatically by PrismLauncher).

---

### B) MultiMC Pre-Launch Command (Still works)

For legacy behavior (or when using **MultiMC** instead of PrismLauncher):

1. Open **MultiMC**.
2. Right-click your instance → **Folder**
3. Place the script inside the opened instance directory
2. Go to your instance's **Settings** → **Custom Commands** tab.
3. Add the following as the **pre-launch command**:

#### Release version (default):

* **Linux/macOS:**

```bash
python3 "$INST_DIR/mc-update.py"
```

* **Windows:**

```cmd
python "%INST_DIR%\\mc-update.py"
```

#### Snapshot version:

```bash
python3 "$INST_DIR/mc-update.py" --snapshot
```

---

## Options

| Option                | Description                                                                  |
| --------------------- | ---------------------------------------------------------------------------- |
| `--release`           | Use the latest release version (default)                                     |
| `--snapshot`          | Use the latest snapshot version                                              |
| `--subprocess_log`    | Enables logging for subprocess patching. Log will be created in instance dir |
| `--prism_path PATH`   | Path to the PrismLauncher or MultiMC binary                                  |
| `--instance_dir PATH` | Manually set the instance folder (default: current working dir)              |
| `--end_up_wrapper`    | All arguments after this will be passed to the actual game launch command    |
| `--help`              | Displays the help text                                                       |

---

## Behavior

* If the instance already has the latest version: it starts normally.
* If an update is needed:
  * The wrapper exits, and a delayed subprocess patches the config and relaunches the instance using PrismLauncher.
* If run as a pre-launch command in MultiMC: the config is patched *before* the launcher starts the game.

---

## FAQ

### What happens if I updated the game manually?

Well it will say it's up to date and do close itself.
Afterwards the game should start as usual.

## Can I compile the script with PyInstaller?

I did not test it.
You can try it it may work but no promises.

## What is the difference between wrapper and pre-command?

Both the **wrapper** and **pre-command** options allow you to run custom scripts before launching Minecraft, but they serve slightly different purposes and are handled differently by **PrismLauncher** and **MultiMC**.

### Pre-Command (Simple)

* **Runs *before* anything else.**
* Executes your script *before* the launcher touches any game files or starts Minecraft.
* Ideal for simple one-shot tasks like updating files or running quick checks.
* **Works well in MultiMC**.
* **⚠ In PrismLauncher, this may not work as expected**, because it applies config changes *after* the pre-command runs, potentially overwriting them.

---

### Wrapper (Advanced – Recommended for PrismLauncher)

* **Replaces the actual Minecraft launch command**.
* **PrismLauncher starts your script *instead of* the game.**
* This script **receives the full game command as arguments**, allowing it to:
  * Check if an update is needed
  * Close cleanly if not (game would run after that)
  * Or relaunch PrismLauncher after patching the version
* More flexible and reliable for complex tasks
* **Required if you want proper version patching in PrismLauncher**, since config changes need to happen *after* Prism’s own logic completes.

---

