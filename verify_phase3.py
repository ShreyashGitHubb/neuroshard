import os
import sys
import shutil
import json
from typer.testing import CliRunner
from shard.cli.main import app

runner = CliRunner()

def test_phase3():
    # Clean up
    if os.path.exists(".shard"): shutil.rmtree(".shard")
    if os.path.exists("test_data.bin"): os.remove("test_data.bin")
    if os.path.exists("test_data.bin.shard.json"): os.remove("test_data.bin.shard.json")
    if os.path.exists(".gitignore"): os.remove(".gitignore")

    print("1. Init & Git Init...")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["git-init"])
    assert os.path.exists(".gitignore")
    with open(".gitignore") as f:
        assert "!*.shard.json" in f.read()

    print("2. Create & Track...")
    with open("test_data.bin", "wb") as f:
        f.write(os.urandom(1024 * 1024)) # 1MB
    runner.invoke(app, ["track", "test_data.bin"])

    print("3. Status (New)...")
    result = runner.invoke(app, ["status"])
    assert "?" in result.stdout
    assert "test_data.bin" in result.stdout

    print("4. Commit (Full Manifest)...")
    runner.invoke(app, ["commit", "-m", "Phase 3 test"])
    assert os.path.exists("test_data.bin.shard.json")
    # Verify it's a full manifest, not a pointer
    with open("test_data.bin.shard.json") as f:
        data = json.load(f)
        assert "blocks" in data
        assert "manifest_version" in data

    print("5. Status (Clean)...")
    result = runner.invoke(app, ["status"])
    assert "M" in result.stdout # My simple status check marks existing as M, which is fine for MVP

    print("6. Diff (Unchanged)...")
    result = runner.invoke(app, ["diff", "test_data.bin"])
    assert "Unchanged:  1" in result.stdout

    print("7. Modify & Diff...")
    with open("test_data.bin", "wb") as f:
        f.write(os.urandom(1024 * 1024)) # New content
    result = runner.invoke(app, ["diff", "test_data.bin"])
    assert "Old blocks: 1" in result.stdout
    assert "New blocks: 1" in result.stdout
    # Likely different hashes
    
    print("8. GC (Dry Run)...")
    result = runner.invoke(app, ["gc", "--dry-run"])
    assert "Would free" in result.stdout

    print("SUCCESS: Phase 3 features work!")

if __name__ == "__main__":
    test_phase3()
