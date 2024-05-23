# Odlanalyzer
Odlanalyzer is a user bahavior analysis tool for OneDrive odl logs. This is based on python3.

## Usage
Odlanalyzer needs to one argument which is input folder path and two options which are output folder path and general keystore folder path. Examples of usages are following :
```
usage: odlanalyzer.py [-h] [-o OUTPUT_FOLDER] [-g GENERAL_KEYSTORE_FOLDER] odl_folder

OneDrive User Behavior analyzer

positional arguments:
  odl_folder            Path to folder with .odl files

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        Output folder
  -g GENERAL_KEYSTORE_FOLDER, --general_keystore_folder GENERAL_KEYSTORE_FOLDER
                        Path to general.keystore (if not in odl_folder)
```
Input folder path is OneDrive odl logs folder path. OneDrive odl logs are stored as binary files with extensions .odl, .odlgz, .odlsent and .aold usually found in the profile folder of a user under the following paths on Windows :

- \AppData\Local\Microsoft\OneDrive\logs\Business1
- \AppData\Local\Microsoft\OneDrive\logs\Personal

Output folder path is user behavior result folder and default path is User_Behavior_Report.

General keystore folder path is a folder which contains general.keystore. It is not necessary to use it if general.keystore is in the OneDrive odl logs folder.
