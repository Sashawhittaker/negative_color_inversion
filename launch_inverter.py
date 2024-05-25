import os
import subprocess

# Get the path to inverter.py
inverter_path = os.path.join(os.path.dirname(__file__), "inverter.py")

# Run inverter.py using subprocess
subprocess.call(["python", inverter_path])