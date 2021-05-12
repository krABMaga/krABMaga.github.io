from shutil import which
from sys import exit
import os
import subprocess
import filecmp
from datetime import datetime
import re
import fileinput
from shutil import copy, copytree

if os.name == "nt":
    os.system('color') # needed on Windows to activate colored terminal text

# template shouldn't be built
BLACKLIST = ["template"]
WHITELIST = None
# todo take input parameters and throw them in whitelist

class termColors:
    RED   = "\033[1;31m"
    YELLOW = "\033[1;33m"
    BLUE  = "\033[1;34m"
    CYAN  = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"

if which("cargo") is None:
    exit(f"{termColors.YELLOW}Cargo must be installed to build the simulations!{termColors.RESET}")

if which("git") is None:
    exit(f"{termColors.RED}Git must be installed to build the simulations!{termColors.RESET}")

if not os.path.exists("config.toml"):
    exit(f"{termColors.RED}You must execute this script from the root folder of the site project!{termColors.RESET}")

# Allows defining the current working directory for a specific scope: https://stackoverflow.com/a/13197763/11826809
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# Clone the examples repo
if not os.path.exists("tmp_examples"):
    print(f"{termColors.CYAN}Examples haven't been cloned yet, cloning now...{termColors.RESET}")
    subprocess.run(["git", "clone", "https://github.com/rust-ab/rust-ab-examples", "tmp_examples"])
else: # Project exists already, try to update it
    print(f"{termColors.CYAN}Updating examples folder...{termColors.RESET}")
    with cd("tmp_examples"):
        pullProcess = subprocess.run(["git", "pull"])
        if pullProcess.returncode != 0:
            exit(f"{termColors.RED}The \"tmp_examples\" folder is in an invalid state (it probably has unstaged changes), delete it!{termColors.RESET}")

dirlist = [
    simulation
    for simulation in os.listdir("tmp_examples")
    if os.path.isdir(os.path.join("tmp_examples",simulation))
    and simulation != ".git"
    and simulation not in BLACKLIST
    and (WHITELIST is None or simulation in WHITELIST)
]

changedSims = set()

# Build wasm and copy benchmark data
for simulation in dirlist:
    with cd(os.path.join("tmp_examples",simulation)):
        print(f"{termColors.CYAN}Building {simulation}...{termColors.RESET}")
        cargoProcess = subprocess.run(["cargo", "make", "build-web", "--profile", "release"])
        # An example failed to build, skip it
        if cargoProcess.returncode != 0:
            print(f"{termColors.YELLOW}Simulation {simulation} failed to build, skipping...{termColors.RESET}")
            continue

        sourceWasmJs = os.path.join("target", "wasm.js")
        sourceWasmBinary = os.path.join("target", "wasm_bg.wasm")
        targetWasmJs = os.path.join("..", "..", "static", "wasm", simulation + ".js")
        targetWasmBinary = os.path.join("..", "..", "static", "wasm", simulation + "_bg.wasm")

        # filecmp compares metadata, which will definitely be different since we just cloned the examples repo. Wasm binaries aren't large, so we just open them and compare the contents.
        if os.path.exists(targetWasmJs) is False or open(sourceWasmJs, "rb").read() == open(targetWasmJs, "rb").read() is False:
            os.rename(os.path.join("target", "wasm.js"), os.path.join("..", "..", "static", "wasm", simulation + ".js"))
            changedSims.add(simulation)

        if os.path.exists(targetWasmBinary) is False or open(sourceWasmBinary, "rb").read() == open(targetWasmBinary, "rb").read() is False:
            os.rename(os.path.join("target", "wasm_bg.wasm"), os.path.join("..", "..", "static", "wasm", simulation + "_bg.wasm"))
            changedSims.add(simulation)

        # update the assets files
        if simulation in changedSims:
            sourceAssets = "assets"
            targetAssets = os.path.join("..", "..", "static", "assets")
            copytree(sourceAssets, targetAssets, dirs_exist_ok=True)
            print(f"{termColors.GREEN}Simulation \"{simulation}\" wasm binaries updated successfully.{termColors.RESET}")

        try:
            for i in os.listdir("bench"):
                sourceCsv = os.path.join("bench", i)
                targetCsvFolder = os.path.join("..", "..", "static", "csv", simulation)
                targetCsv = os.path.join(targetCsvFolder, i)
                if os.path.exists(targetCsv) is False or open(sourceCsv, "rb").read() == open(targetCsv, "rb").read() is False:
                    if not os.path.exists(targetCsvFolder):
                        os.mkdir(targetCsvFolder) # copy does not automatically create intermediary folders
                    copy(sourceCsv, targetCsv)
                    changedSims.add(simulation)
            print(f"{termColors.GREEN}Benchmarks found for simulation \"{simulation}\"!{termColors.RESET}")
        except FileNotFoundError:
            print(f"{termColors.YELLOW}Benchmarks not found for simulation \"{simulation}\"!{termColors.RESET}")
    print(f"{termColors.GREEN}Simulation {simulation} processed successfully.{termColors.RESET}")

# update the changed simulations markdown files last_updated variable and set it to today
for sim in changedSims:
    simContent = os.path.join("content", sim + ".md")
    # This simulation may not yet have an associated markdown file, in this case skip it.
    if not os.path.exists(simContent):
        print(f'{termColors.YELLOW}Simulation "{sim}" does not have an associated markdown file, skipping last_updated job...{termColors.RESET}')
        continue

    r = re.compile('last_updated = (.*)')
    for line in fileinput.input(simContent, inplace=True):
      match = r.match(line)
      print('last_updated = "' + datetime.today().strftime('%Y-%m-%d') + '"' if match else line.replace('\n', ''))

if len(changedSims) > 0:
    print(f"{termColors.GREEN}Simulations updated: " + ", ".join(changedSims) + f"{termColors.RESET}")
else:
    print(f"{termColors.GREEN}No simulations updated.{termColors.RESET}")
