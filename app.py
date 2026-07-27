import sys, os
# Add src directory to path
sys.path.insert(0, os.path.abspath("src"))

from skylark_signal.ui.app_shell import run_app_shell

if __name__ == "__main__":
    run_app_shell()
