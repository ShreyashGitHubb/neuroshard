# 🧠 NeuroShard

[![PyPI version](https://badge.fury.io/py/neuroshard.svg)](https://badge.fury.io/py/neuroshard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **"Git for AI models. Fast. Deduplicated. Reproducible."**

NeuroShard is the missing link in your MLOps stack. It’s a **content-addressed version control system** built specifically for large AI models and datasets.

Stop treating your 10GB model checkpoints like binary blobs. Treat them like code.

---

## 🛑 The Problem

**Git LFS is broken for AI.**
- **Storage Bloat**: Change 1 byte in a 10GB file? Git LFS stores a *new* 10GB file.
- **Slow Clones**: Pulling a repo means pulling massive files you might not even need.
- **Opaque History**: You can't see *what* changed in your model, only that it changed.

## ✨ The NeuroShard Solution

NeuroShard uses **Content-Defined Chunking (CDC)** to split your massive files into small, deduplicated blocks.

- **Smart**: It knows when you only changed a small part of your model (like fine-tuning a few layers).
- **Efficient**: It **only uploads the unique chunks**. If 90% of your model is unchanged, you save 90% bandwidth and storage.
- **Reproducible**: Manifests are small JSON files committed to Git. Your code and data are finally in sync.

---

## ⚡ 30-Second Magic

Don't believe it? Watch this.

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

**You just saved 9.85 GB of upload bandwidth.**

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

## 🚀 Quickstart

### 1. Initialize
```bash
cd my-project
nshard init
nshard git-init  # Configures .gitignore to ignore large files but track manifests
```

### 2. Track & Commit
```bash
nshard track weights/model.pt
nshard commit -m "Add model"
```

### 3. Push Data (To Storage)
```bash
# Start a local server for testing (or use S3/GCS in prod)
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

---

<p align="center">
  Made with ❤️ by Shreyash
</p>
