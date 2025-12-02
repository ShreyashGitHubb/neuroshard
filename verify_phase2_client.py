import os
import sys
import shutil
import hashlib
import requests
from typer.testing import CliRunner
from shard.cli.main import app

runner = CliRunner()
SERVER_URL = "http://localhost:8000"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def test_flow():
    # Clean up
    if os.path.exists(".shard"): shutil.rmtree(".shard")
    if os.path.exists("test_data_remote.bin"): os.remove("test_data_remote.bin")
    if os.path.exists("test_data_remote.bin.shard.json"): os.remove("test_data_remote.bin.shard.json")

    print("1. Init...")
    runner.invoke(app, ["init"])

    print("2. Create & Commit...")
    with open("test_data_remote.bin", "wb") as f:
        f.write(os.urandom(5 * 1024 * 1024)) # 5MB
    original_hash = sha256_file("test_data_remote.bin")
    
    runner.invoke(app, ["track", "test_data_remote.bin"])
    runner.invoke(app, ["commit", "-m", "Remote test"])
    
    print("3. Push...")
    result = runner.invoke(app, ["push", "--remote", SERVER_URL])
    if result.exit_code != 0:
        print(result.stdout)
        sys.exit(1)

    print("4. Simulate fresh clone...")
    shutil.copy("test_data_remote.bin.shard.json", "pointer.json")
    shutil.rmtree(".shard")
    os.remove("test_data_remote.bin")
    os.remove("test_data_remote.bin.shard.json")
    shutil.copy("pointer.json", "test_data_remote.bin.shard.json")

    print("5. Pull...")
    result = runner.invoke(app, ["pull", "test_data_remote.bin.shard.json", "--remote", SERVER_URL])
    if result.exit_code != 0:
        print(result.stdout)
        sys.exit(1)

    print("6. Verify...")
    restored_hash = sha256_file("test_data_remote.bin")
    if original_hash == restored_hash:
        print("SUCCESS: Remote sync works!")
    else:
        print("FAILURE: Hashes mismatch!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        requests.get(f"{SERVER_URL}/docs")
    except:
        print("Server not running!")
        sys.exit(1)
    test_flow()
