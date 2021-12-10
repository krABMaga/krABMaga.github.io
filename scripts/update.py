from shutil import which
from sys import exit
import os
import subprocess
from datetime import datetime
import re
import fileinput
from shutil import copy, copytree
import argparse

if os.name == "nt":
    os.system('color')  # needed on Windows to activate colored terminal text

# template shouldn't be built and the .github folder is not an example
BLACKLIST = ["template", ".github", "wsg_model_exploration"]
WHITELIST = None

parser = argparse.ArgumentParser(description='Update the wasm builds and chart data related to the simulations.')
parser.add_argument('simulations', metavar='S', type=str, nargs='*',
                    help='the name of the specific simulation to check')

args = parser.parse_args()
WHITELIST = args.simulations


class OutputHandler:

    # Special terminal color codes, used if we're running the script in a local environment
    RED = "\033[1;31m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"

    def __init__(self):
        self.github_runner = os.environ.get('GITHUB_ACTIONS')
        self.info(f"Running in a GitHub runner environment: {True if self.github_runner else False}")

    def print(self, message_type: str, message: str):
        if self.github_runner:
            print(f"::{message_type} ::{message}")
        else:
            color = OutputHandler.YELLOW if type == "warning" else OutputHandler.RED
            print(f"{color}{message}{OutputHandler.RESET}")

    def error(self, message: str):
        self.print("error", message)
        exit(1)

    def warning(self, message: str):
        self.print("warning", message)

    @staticmethod
    def info(message: str):
        print(f"{OutputHandler.CYAN}{message}{OutputHandler.RESET}")

    @staticmethod
    def success(message: str):
        print(f"{OutputHandler.GREEN}{message}{OutputHandler.RESET}")

    class Group:
        def __init__(self, group_title: str):
            self.github_runner = os.environ.get('GITHUB_ACTIONS')
            self.group_title = group_title

        def __enter__(self):
            if self.github_runner:
                print(f"::group::{self.group_title}")

        def __exit__(self, etype, value, traceback):
            if self.github_runner:
                print("::endgroup::")


# Allows defining the current working directory for a specific scope: https://stackoverflow.com/a/13197763/11826809
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


outputHandler = OutputHandler()

if which("cargo") is None:
    outputHandler.error("Cargo must be installed to build the simulations!")

if which("git") is None:
    outputHandler.error("Git must be installed to build the simulations!")

if not os.path.exists("config.toml"):
    outputHandler.error("You must execute this script from the root folder of the site project!")

with outputHandler.Group("Installing cargo-make"):
    cargoMakeInstall = subprocess.run(["cargo", "install", "cargo-make"])
    if cargoMakeInstall.returncode != 0:
        outputHandler.error("Cargo-make failed to install!")

# Clone the examples repo
if not os.path.exists("tmp_examples"):
    outputHandler.info("Examples haven't been cloned yet, cloning now...")
    with outputHandler.Group("Clone examples repository"):
        subprocess.run(["git", "clone", "https://github.com/rust-ab/rust-ab-examples", "tmp_examples"])
else:  # Project exists already, try to update it
    outputHandler.info("Updating examples folder...")
    with cd("tmp_examples"):
        with outputHandler.Group("Update examples repository"):
            pullProcess = subprocess.run(["git", "pull"])
            if pullProcess.returncode != 0:
                outputHandler.error("The \"tmp_examples\" folder is in an invalid state (it probably has unstaged "
                                    "changes), delete it!")
        with outputHandler.Group("Forcing a specific branch"):
            pullProcess = subprocess.run(["git", "checkout", "visualization"])
            if pullProcess.returncode != 0:
                outputHandler.error("The checkout step failed!")


dirlist = [
    simulation
    for simulation in os.listdir("tmp_examples")
    if os.path.isdir(os.path.join("tmp_examples", simulation))
    and simulation != ".git"
    and simulation not in BLACKLIST
    and (not WHITELIST or simulation in WHITELIST)
]

changedSims = set()

# Build wasm and copy benchmark data
for simulation in dirlist:
    with cd(os.path.join("tmp_examples", simulation)):
        with outputHandler.Group("Applying bevy_log wasm hotfix"):
            pullProcess = subprocess.run(["cargo", "update", "-p", "tracing-wasm", "--precise", "0.2.0"])
            if pullProcess.returncode != 0:
                outputHandler.error("The bevy_log hotfix step failed!")
        outputHandler.info(f"Building {simulation}...")
        with outputHandler.Group(f"Build {simulation} wasm"):
            cargoProcess = subprocess.run(["cargo", "make", "--profile", "release", "build-web"])
            # An example failed to build, skip it
            if cargoProcess.returncode != 0:
                outputHandler.warning(f"Simulation {simulation} failed to build, skipping...")
                continue

        sourceWasmJs = os.path.join("target", "wasm.js")
        sourceWasmBinary = os.path.join("target", "wasm_bg.wasm")
        targetWasmJs = os.path.join("..", "..", "static", "wasm", simulation + ".js")
        targetWasmBinary = os.path.join("..", "..", "static", "wasm", simulation + "_bg.wasm")

        # filecmp compares metadata, which will definitely be different since we just cloned the examples repo. Wasm
        # binaries aren't large, so we just open them and compare the contents.
        if (os.path.exists(targetWasmJs) is False or
                (open(sourceWasmJs, "rb").read() == open(targetWasmJs, "rb").read()) is False):
            os.replace(sourceWasmJs, targetWasmJs)
            changedSims.add(simulation)

        if (os.path.exists(targetWasmBinary) is False or
                (open(sourceWasmBinary, "rb").read() == open(targetWasmBinary, "rb").read()) is False):
            os.replace(sourceWasmBinary, targetWasmBinary)
            changedSims.add(simulation)

        # update the assets files
        if simulation in changedSims:
            sourceAssets = "assets"
            targetAssets = os.path.join("..", "..", "static", "assets")
            copytree(sourceAssets, targetAssets, dirs_exist_ok=True)
            outputHandler.success(f"Simulation \"{simulation}\" wasm binaries updated successfully.")

        try:
            for i in os.listdir(os.path.join("benches", "results")):
                sourceCsv = os.path.join("benches", "results", i)
                targetCsvFolder = os.path.join("..", "..", "static", "csv", simulation)
                targetCsv = os.path.join(targetCsvFolder, i)
                if (os.path.exists(targetCsv) is False or
                        (open(sourceCsv, "rb").read() == open(targetCsv, "rb").read()) is False):
                    if not os.path.exists(targetCsvFolder):
                        os.mkdir(targetCsvFolder)  # copy does not automatically create intermediary folders
                    copy(sourceCsv, targetCsv)
                    changedSims.add(simulation)
            outputHandler.success(f"Benchmarks found for simulation \"{simulation}\"!")
        except FileNotFoundError:
            outputHandler.warning(f"Benchmarks not found for simulation \"{simulation}\"!")
    outputHandler.success(f"Simulation {simulation} processed successfully.")

# update the changed simulations markdown files last_updated variable and set it to today
for sim in changedSims:
    simContent = os.path.join("content", sim + ".md")
    # This simulation may not yet have an associated markdown file, in this case skip it.
    if not os.path.exists(simContent):
        outputHandler.warning(f"Simulation \"{sim}\" does not have an associated markdown file, skipping last_updated "
                              f"job...")
        continue

    r = re.compile('last_updated = (.*)')
    for line in fileinput.input(simContent, inplace=True):
        match = r.match(line)
        print('last_updated = "' + datetime.today().strftime('%Y-%m-%d') + '"' if match else line.replace('\n', ''))

if len(changedSims) > 0:
    outputHandler.success("Simulations updated: " + ", ".join(changedSims))
else:
    outputHandler.success("No simulations updated.")
