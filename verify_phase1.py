import os
import sys
import hashlib
import shutil
from typer.testing import CliRunner
from shard.cli.main import app

runner = CliRunner()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def test_flow():
    # Clean up
    if os.path.exists(".shard"):
        shutil.rmtree(".shard")
    if os.path.exists("test_data.bin"):
        os.remove("test_data.bin")
    if os.path.exists("test_data.bin.shard.json"):
        os.remove("test_data.bin.shard.json")

    print("1. Init...")
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert os.path.exists(".shard")

    print("2. Create test file...")
    # Create 10MB random file
    with open("test_data.bin", "wb") as f:
        f.write(os.urandom(10 * 1024 * 1024))
    original_hash = sha256_file("test_data.bin")
    print(f"Original Hash: {original_hash}")

    print("3. Track...")
    result = runner.invoke(app, ["track", "test_data.bin"])
    assert result.exit_code == 0

    print("4. Commit...")
    result = runner.invoke(app, ["commit", "-m", "Initial commit"])
    assert result.exit_code == 0
    assert os.path.exists("test_data.bin.shard.json")

    print("5. Delete original file...")
    os.remove("test_data.bin")
    assert not os.path.exists("test_data.bin")

    print("6. Checkout...")
    result = runner.invoke(app, ["checkout", "test_data.bin.shard.json"])
    assert result.exit_code == 0
    assert os.path.exists("test_data.bin")

    print("7. Verify...")
    restored_hash = sha256_file("test_data.bin")
    print(f"Restored Hash: {restored_hash}")
    
    if original_hash == restored_hash:
        print("SUCCESS: Hashes match!")
    else:
        print("FAILURE: Hashes do not match!")
        sys.exit(1)

if __name__ == "__main__":
    test_flow()
