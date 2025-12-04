# 🧠 NeuroShard

> **Git for AI models. Fast. Deduplicated. Reproducible.**

[![PyPI version](https://badge.fury.io/py/neuroshard.svg)](https://badge.fury.io/py/neuroshard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**NeuroShard** is the missing link in your MLOps stack. It’s a content-addressed version control system built specifically for large AI models and datasets.

---

## ⚡ TL;DR (Minimal Quickstart)

Install and track your first model in 30 seconds:

```bash
pip install neuroshard

# Initialize and track a file
nshard init
nshard track models/my-large-model.pth
nshard commit -m "Initial checkpoint"
```

---

## 🛑 The Problem

**Git LFS is broken for AI.**
- **Storage Bloat**: Change 1 byte in a 10GB file? Git LFS stores a *new* 10GB file.
- **Slow Clones**: Pulling a repo means pulling massive files you might not even need.
- **Opaque History**: You can't see *what* changed in your model, only that it changed.

## ✨ Features (The Solution)

NeuroShard uses **Content-Defined Chunking (CDC)** to split your massive files into small, deduplicated blocks.

- **Smart Deduplication**: Only uploads unique chunks. If 90% of your model is unchanged, you save 90% bandwidth.
- **Efficient Storage**: Stores changes (deltas) rather than full blobs.
- **Git Integration**: Manifests are small JSON files committed to Git. Code and data stay in sync.
- **Storage Agnostic**: Works with local storage and HTTP remotes (S3 coming soon).

---

## ⚡ 30-Second Magic (Demo)

See how NeuroShard saves bandwidth when fine-tuning a model:

```bash
# 1. Track your massive model
$ nshard track models/gpt-finetune.pth
[+] Tracking models/gpt-finetune.pth

# 2. First Commit (Initial Upload)
$ nshard commit -m "Initial checkpoint"
[+] Chunking... 100% (2560/2560 blocks)
[+] Uploading... 10.0 GB sent.
[+] Created manifest: models/gpt-finetune.pth.shard.json

# --- YOU FINE-TUNE THE MODEL (Only weights change) ---

# 3. Second Commit (The Magic)
$ nshard commit -m "Finetuned epoch 1"
[+] Chunking... 100% (2560/2560 blocks)
[+] Deduplicating...
[+] Uploading... 150 MB sent. (98.5% Savings!) 🚀
```

**Result: You just saved 9.85 GB of upload bandwidth.**

---

## 🆚 Why NeuroShard?

| Feature | 🧠 NeuroShard | 🐢 Git LFS | 🤗 HuggingFace |
| :--- | :--- | :--- | :--- |
| **Deduplication** | ✅ **Block-level** (Global) | ❌ File-level | ❌ File-level |
| **Storage Cost** | 📉 **Minimal** (Deltas only) | 📈 Full Blobs | 📈 Full Blobs |
| **Speed** | ⚡ **Instant** (Push diffs) | 🐢 Slow (Push all) | 🐢 Slow |
| **Privacy** | 🔒 **Self-hosted** / Any Remote | 🔒 Self-hosted | ☁️ Cloud / Public |
| **Integrity** | 🛡️ **SHA-256** Verified | ⚠️ Pointer based | ⚠️ Pointer based |

---

## 📦 Installation

```bash
pip install neuroshard
```

## 🚀 Usage Guide

### 1. Initialize
```bash
cd my-project
nshard init
nshard git-init  # Configures .gitignore
```

### 2. Track & Commit
```bash
nshard track weights/model.pt
nshard commit -m "Add model"
```

### 3. Push Data (To Storage)
```bash
# Start a local server for testing
python -m shard.server.app &

nshard push --remote http://localhost:8000
```

### 4. Push Manifests (To Git)
```bash
git add weights/model.pt.shard.json
git commit -m "Add model weights"
git push origin main
```

---

## 🛠 CLI Reference

| Command | Description |
| :--- | :--- |
| `nshard init` | Initialize a new NeuroShard repo. |
| `nshard track <file>` | Start tracking a large file. |
| `nshard commit` | Chunk, deduplicate, and create a manifest. |
| `nshard push` | Upload unique blocks to the remote. |
| `nshard pull` | Download blocks and reconstruct files. |
| `nshard checkout` | Restore the original file from a manifest. |
| `nshard diff` | See exactly how many blocks changed. |
| `nshard gc` | Clean up unused blocks to free space. |

---

## 🤝 Contributing

We are building the future of AI version control. Join us.

1. Fork the repo.
2. Create a branch.
3. Submit a PR.

Run tests:
```bash
python -m unittest discover tests
```

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ by Shreyash
</p>
