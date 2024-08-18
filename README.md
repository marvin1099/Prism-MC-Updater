# Prism-MC-Updater
## Description
A simple Python script for automatically updating Minecraft profiles in MultiMC/Prism Launcher.  
This script ensures your instance always runs the latest release or snapshot version of Minecraft.

## Installation
Download the script from one of the following sources:

- [Codeberg Releases](https://codeberg.org/marvin1099/MultiMC-LatestVer/releases)
- [GitHub Releases](https://github.com/marvin1099/MultiMC-LatestVer/releases)

## Requirements
- Python installed on your system
- MultiMC or Prism Launcher installed

## Setup
1. Ensure you have a Minecraft instance created in MultiMC/Prism Launcher.
2. Place the script in the root directory of your instance.  
   This folder should also contain the `mmc-pack.json` file.
3. By default, the script updates to the latest release version of Minecraft.  
   If you prefer to use the latest snapshot,  
   change the `USE_LATEST_RELEASE` variable in the script from `True` to `False`,  
   or use the `snapshot` argument during execution.

## Usage
1. Open MultiMC/Prism Launcher.
2. Navigate to the instance settings of the instance you wish to auto update.
3. Go to the `Settings` tab, then open the `Custom Commands` sub-tab.
4. Add the following command as a pre-launch command:
   - **Linux/Mac:** `python "$INST_DIR/mc-update.py"`
   - **Windows:** `python "$INST_DIR\\mc-update.py"`
5. To update to the latest snapshot instead of the release,  
   without changing the variable inside the script,  
   add the word `snapshot` as argument:
   - **Linux/Mac:** `python "$INST_DIR/mc-update.py" snapshot`
   - **Windows:** `python "$INST_DIR\\mc-update.py" snapshot`

## Running the Script
After setup, every time you start the instance in MultiMC/Prism Launcher,  
the script will automatically update Minecraft to the latest version,  
for release or snapshot and launch the game as usual.
