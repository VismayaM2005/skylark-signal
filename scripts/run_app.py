import os, sys, subprocess

def main():
    print("=== STARTING SKYLARK SIGNAL STREAMLIT APP ===")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
