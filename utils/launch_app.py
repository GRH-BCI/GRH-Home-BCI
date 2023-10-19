import subprocess
import os
from subprocess import PIPE

def launch_app(application: str):
    if application.strip() == "BCI Paint":
        subprocess.Popen(["start", os.path.join("BCI-Paint", "dist", "main.exe")], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

        """
            open the paint application window
        """
    elif application == "BCI Gaming":
        if application.strip() == "BCI Gaming":
            subprocess.Popen(["start", os.path.join("BCI-Gaming-Platform", "win-unpacked", "grh_bci_gaming_platform.exe")], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

    elif application == "manual":
        if application.strip() == "manual":
            subprocess.run(
                ["start", os.path.join("Assets", "manual.pdf")],
                capture_output=True, shell=True)


