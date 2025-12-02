import typer
import os
import sys
from typing import Optional
from shard.core.store import LocalStore
from shard.core.chunker import chunk_file, decompress_chunk
from shard.core.manifest import create_manifest
from shard.core.index import Index
from shard.core.remote import RemoteClient
import json

app = typer.Typer()

@app.command()
def push(remote: str = typer.Option(..., help="Remote server URL")):
    """Push tracked files to a remote server."""
    index = Index()
    tracked_files = index.load()
    
    if not tracked_files:
        typer.echo("Nothing to push.")
        return

    client = RemoteClient(remote)
    store = LocalStore()
    
    for file_path in tracked_files:
        pointer_path = f"{file_path}.shard.json"
        if not os.path.exists(pointer_path):
            typer.echo(f"Skipping {file_path} (no pointer found, commit first)")
            continue
            
        with open(pointer_path, "r") as f:
            pointer = json.load(f)
        manifest_hash = pointer["manifest"]
        
        # Read manifest
        try:
            manifest_bytes = store.read_manifest(manifest_hash)
            manifest = json.loads(manifest_bytes)
        except FileNotFoundError:
            typer.echo(f"Error: Manifest {manifest_hash} missing locally.")
            continue
            
        typer.echo(f"Pushing {file_path}...")
        
        # Upload blocks
        for block in manifest["blocks"]:
            h = block["hash"]
            if not client.has_block(h):
                # typer.echo(f"  Uploading block {h[:8]}...")
                data = store.read_object(h)
                client.upload_block(h, data)
        
        # Upload manifest
        client.upload_manifest(manifest_hash, manifest_bytes)
        typer.echo(f"Pushed {file_path} -> {manifest_hash}")

@app.command()
def pull(pointer_file: str, remote: str = typer.Option(..., help="Remote server URL")):
    """Pull a file from a remote server."""
    if not pointer_file.endswith(".shard.json"):
        typer.echo("Error: Input must be a .shard.json pointer file.")
        raise typer.Exit(code=1)
        
    with open(pointer_file, "r") as f:
        pointer = json.load(f)
    manifest_hash = pointer["manifest"]
    
    client = RemoteClient(remote)
    store = LocalStore()
    store.init() # Ensure dirs exist
    
    # Download manifest
    typer.echo(f"Fetching manifest {manifest_hash}...")
    try:
        manifest_bytes = client.download_manifest(manifest_hash)
        store.write_manifest(manifest_hash, manifest_bytes)
        manifest = json.loads(manifest_bytes)
    except Exception as e:
        typer.echo(f"Error fetching manifest: {e}")
        raise typer.Exit(code=1)
        
    # Download blocks
    typer.echo(f"Fetching blocks for {manifest['file_path']}...")
    for block in manifest["blocks"]:
        h = block["hash"]
        if not store.has_object(h):
            # typer.echo(f"  Downloading block {h[:8]}...")
            data = client.download_block(h)
            store.write_object(h, data)
            
    # Reconstruct
    typer.echo("Reconstructing file...")
    original_path = manifest["file_path"]
    with open(original_path, "wb") as f:
        for block in manifest["blocks"]:
            compressed = store.read_object(block["hash"])
            data = decompress_chunk(compressed)
            f.write(data)
            
    typer.echo("Done.")


@app.command()
def status():
    """Show status of tracked files."""
    index = Index()
    tracked_files = index.load()
    
    if not tracked_files:
        typer.echo("No tracked files.")
        return
        
    typer.echo("Tracked files:")
    for path in tracked_files:
        status = " "
        if not os.path.exists(path):
            status = "D" # Deleted
        elif not os.path.exists(f"{path}.shard.json"):
            status = "?" # Untracked/New
        else:
            status = "M" # Modified (potentially - simplified check)
            # Real check would compare hashes
            
        typer.echo(f" {status} {path}")

@app.command()
def diff(path: str):
    """Show block-level diff for a file."""
    if not os.path.exists(path):
        typer.echo(f"File {path} not found.")
        return
        
    manifest_path = f"{path}.shard.json"
    if not os.path.exists(manifest_path):
        typer.echo(f"No commit found for {path}.")
        return
        
    with open(manifest_path, "rb") as f:
        manifest = json.load(f)
    
    current_blocks = chunk_file(path)
    old_blocks = manifest["blocks"]
    
    old_hashes = {b["hash"] for b in old_blocks}
    new_hashes = {b["hash"] for b in current_blocks}
    
    common = old_hashes.intersection(new_hashes)
    added = new_hashes - old_hashes
    removed = old_hashes - new_hashes
    
    typer.echo(f"Diff for {path}:")
    typer.echo(f"  Old blocks: {len(old_blocks)}")
    typer.echo(f"  New blocks: {len(current_blocks)}")
    typer.echo(f"  Unchanged:  {len(common)}")
    typer.echo(f"  Added:      {len(added)}")
    typer.echo(f"  Removed:    {len(removed)}")
    
    if len(current_blocks) > 0:
        change_pct = (len(added) / len(current_blocks)) * 100
        typer.echo(f"  Change:     {change_pct:.1f}%")



@app.command()
def gc(dry_run: bool = False):
    """Garbage collect unused blocks."""
    from shard.core.gc import collect_garbage
    bytes_freed, count = collect_garbage(dry_run=dry_run)
    if dry_run:
        typer.echo(f"Would free {bytes_freed} bytes ({count} objects).")
    else:
        typer.echo(f"Freed {bytes_freed} bytes ({count} objects).")

@app.command()
def git_init():
    """Configure Git to ignore .shard but track manifests."""
    gitignore_path = ".gitignore"
    content = "\n# Shard\n.shard/\n!*.shard.json\n"
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "a") as f:
            f.write(content)
    else:
        with open(gitignore_path, "w") as f:
            f.write(content)
            
    typer.echo("Updated .gitignore for Shard.")

@app.command()
def init():

    """Initialize a new Shard repository."""
    store = LocalStore()
    store.init()
    typer.echo("Initialized empty Shard repository in .shard/")

@app.command()
def track(path: str):
    """Start tracking a file."""
    if not os.path.exists(path):
        typer.echo(f"Error: File {path} not found.")
        raise typer.Exit(code=1)
    
    index = Index()
    index.add(path)
    typer.echo(f"Tracking {path}")

@app.command()
def commit(message: str = typer.Option(..., "-m", "--message", help="Commit message")):
    """Commit tracked files."""
    index = Index()
    tracked_files = index.load()
    
    if not tracked_files:
        typer.echo("Nothing to commit (no tracked files).")
        return

    store = LocalStore()
    
    for file_path in tracked_files:
        if not os.path.exists(file_path):
            typer.echo(f"Warning: Tracked file {file_path} missing, skipping.")
            continue
            
        typer.echo(f"Chunking {file_path}...")
        blocks = chunk_file(file_path)
        
        # Store blocks
        for block in blocks:
            store.write_object(block["hash"], block["data"])
            
        # Create manifest
        meta = {"message": message}
        mhash, manifest, manifest_bytes = create_manifest(file_path, blocks, meta)
        store.write_manifest(mhash, manifest_bytes)
        
        # Write full manifest to workspace file (Git-friendly)
        manifest_path = f"{file_path}.shard.json"
        with open(manifest_path, "wb") as f:
            f.write(manifest_bytes)
            
        typer.echo(f"Committed {file_path} -> {mhash}")
        typer.echo(f"Updated manifest: {manifest_path}")

@app.command()
def checkout(manifest_file: str):
    """Restore a file from its manifest file."""
    if not manifest_file.endswith(".shard.json"):
        typer.echo("Error: Input must be a .shard.json manifest file.")
        raise typer.Exit(code=1)
        
    if not os.path.exists(manifest_file):
        typer.echo(f"Error: Manifest file {manifest_file} not found.")
        raise typer.Exit(code=1)
        
    import json
    with open(manifest_file, "rb") as f:
        manifest = json.load(f)
        
    store = LocalStore()
    original_path = manifest["file_path"]
    typer.echo(f"Restoring {original_path}...")
    
    with open(original_path, "wb") as f:
        for block in manifest["blocks"]:
            try:
                compressed = store.read_object(block["hash"])
                data = decompress_chunk(compressed)
                f.write(data)
            except FileNotFoundError:
                typer.echo(f"Error: Block {block['hash']} missing locally.")
                typer.echo("Try running: shard pull " + manifest_file + " --remote <url>")
                raise typer.Exit(code=1)
                
    typer.echo("Done.")

@app.command()
def push(remote: str = typer.Option(..., help="Remote server URL")):
    """Push tracked files to a remote server."""
    index = Index()
    tracked_files = index.load()
    
    if not tracked_files:
        typer.echo("Nothing to push.")
        return

    client = RemoteClient(remote)
    store = LocalStore()
    
    for file_path in tracked_files:
        manifest_path = f"{file_path}.shard.json"
        if not os.path.exists(manifest_path):
            typer.echo(f"Skipping {file_path} (no manifest found, commit first)")
            continue
            
        with open(manifest_path, "rb") as f:
            manifest_bytes = f.read()
            manifest = json.loads(manifest_bytes)
        
        # We re-compute hash to ensure integrity or just trust the file? 
        # For now, let's trust the file content is the manifest.
        # But we need the hash for the remote PUT.
        import hashlib
        mhash = hashlib.sha256(manifest_bytes).hexdigest()
            
        typer.echo(f"Pushing {file_path}...")
        
        # Upload blocks
        for block in manifest["blocks"]:
            h = block["hash"]
            if not client.has_block(h):
                # typer.echo(f"  Uploading block {h[:8]}...")
                try:
                    data = store.read_object(h)
                    client.upload_block(h, data)
                except FileNotFoundError:
                     typer.echo(f"Error: Block {h} missing locally, cannot push.")
                     continue
        
        # Upload manifest
        client.upload_manifest(mhash, manifest_bytes)
        typer.echo(f"Pushed {file_path} -> {mhash}")

@app.command()
def pull(manifest_file: str, remote: str = typer.Option(..., help="Remote server URL")):
    """Pull missing blocks for a manifest."""
    if not manifest_file.endswith(".shard.json"):
        typer.echo("Error: Input must be a .shard.json manifest file.")
        raise typer.Exit(code=1)
        
    with open(manifest_file, "rb") as f:
        manifest = json.load(f)
    
    client = RemoteClient(remote)
    store = LocalStore()
    store.init() 
    
    # Download blocks
    typer.echo(f"Fetching blocks for {manifest['file_path']}...")
    for block in manifest["blocks"]:
        h = block["hash"]
        if not store.has_object(h):
            # typer.echo(f"  Downloading block {h[:8]}...")
            data = client.download_block(h)
            store.write_object(h, data)
            
    typer.echo("All blocks present.")

if __name__ == "__main__":
    app()
