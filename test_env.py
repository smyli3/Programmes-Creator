import sys
import os
import platform

def test_environment():
    print("=== Python Environment Test ===")
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Platform: {platform.platform()}")
    
    # Test file access
    test_file = "Report CXV.csv"
    print(f"\nTesting access to: {test_file}")
    if os.path.exists(test_file):
        print("File exists!")
        print(f"File size: {os.path.getsize(test_file)} bytes")
    else:
        print("File not found!")
    
    # List files in directory
    print("\nFiles in current directory:")
    for f in os.listdir('.'):
        if os.path.isfile(f):
            print(f"- {f} ({os.path.getsize(f)} bytes)")

if __name__ == "__main__":
    test_env()
