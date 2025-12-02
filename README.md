# Shard

**Shard — Content-Addressed, Chunked Model Versioning**

> "Git for AI models. Fast. Deduplicated. Reproducible."

Shard is a version control system designed specifically for large AI models and datasets. It solves the "Git LFS problem" by splitting large files into deduplicated, compressed chunks (shards) and storing only the changes. Manifests are small JSON files that track these chunks and are committed directly to Git, ensuring perfect reproducibility.

## 🚀 Key Features

- **⚡ Fast Incremental Pushes**: Only upload changed chunks (4MB blocks).
- **🧱 Deduplication**: Store unique blocks once, across all model versions.
- **🔒 Integrity**: SHA-256 verification for every block.
- **📝 Git Integration**: Manifests live in Git; data lives in Shard.
- **🧰 Storage Agnostic**: Works with local storage and HTTP remotes (S3 coming soon).

## 📦 Installation

```bash
pip install -e .
```

## ⚡ Quickstart

### 1. Initialize
Initialize a Shard repository in your project. This sets up the `.shard` directory.

```bash
shard init
shard git-init  # Configures .gitignore
```

### 2. Track a Model
Tell Shard to track your large model files.

```bash
shard track models/resnet50.pth
```

### 3. Commit
Chunk the file, compute hashes, and create a manifest.

```bash
shard commit -m "Initial checkpoint"
```
This creates a `models/resnet50.pth.shard.json` file. **Commit this JSON file to Git.**

```bash
git add models/resnet50.pth.shard.json
git commit -m "Add model checkpoint"
```

### 4. Push to Remote
Upload your shards to a remote server.

```bash
shard push --remote http://localhost:8000
```

### 5. Pull and Checkout
On another machine, pull the blocks and reconstruct the file.

```bash
shard pull models/resnet50.pth.shard.json --remote http://localhost:8000
shard checkout models/resnet50.pth.shard.json
```

## 🛠 CLI Commands

- `shard init`: Initialize a new Shard repo.
- `shard track <file>`: Start tracking a file.
- `shard commit -m <msg>`: Chunk and commit tracked files.
- `shard status`: Show status of tracked files.
- `shard diff <file>`: Show block-level diff stats.
- `shard push`: Push to remote.
- `shard pull`: Pull from remote.
- `shard gc`: Garbage collect unused blocks.

## 🤝 Contributing

Contributions are welcome! Please run tests before submitting a PR.

```bash
python -m unittest discover tests
```

## 📜 License

MIT
