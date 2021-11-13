#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
from pathlib import Path
import subprocess

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Installer of systemd service.")
    parser.add_argument("-c", dest="config", required=True, help="Path of the configuration file.")
    parser.add_argument("--python", dest="python", default="/usr/bin/python3", help="Path of the python.")
    args = parser.parse_args()

    # Project root directory
    basedir = Path(__file__).parent.resolve()

    # Install the systemd service and replace the relevant variables
    inputFile = basedir.joinpath("systemd/hilldustWrapper.service")
    inputContent = Path(inputFile).read_text()
    inputContent = inputContent.replace("PYTHON_PATH", args.python)
    inputContent = inputContent.replace("SCRIPT_PATH", str(basedir.joinpath("hilldustWrapper.py")))
    inputContent = inputContent.replace("CONFIG_PATH", args.config)
    f = open("/etc/systemd/system/hilldustWrapper.service", "w")
    f.write(inputContent)
    f.close()

    # Enable and start the service
    subprocess.check_call("systemctl daemon-reload", shell=True)
    subprocess.check_call("systemctl enable hilldustWrapper --now", shell=True)

if __name__ == "__main__":
    main()
