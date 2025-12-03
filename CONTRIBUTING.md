# Contributing to NeuroShard

Thank you for your interest in contributing to NeuroShard! We welcome contributions from everyone.

## Development Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ShreyashGitHubb/MedScan-AI.git
    cd MedScan-AI
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -e .[dev]
    pip install -r requirements-dev.txt  # If exists
    ```

## Project Structure

- `src/neuroshard/`: Main source code.
    - `cli.py`: CLI entry point.
    - `commands/`: Individual CLI commands.
    - `core/`: Core logic (chunking, storage, manifests).
    - `server/`: Remote server implementation.
- `tests/`: Unit and integration tests.
- `examples/`: Example scripts and data.

## Running Tests

```bash
python -m unittest discover tests
```

## Code Style

- We follow PEP 8.
- Please run `black .` before submitting a PR.
- Ensure all tests pass.

## Pull Request Process

1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  Ensure the test suite passes.
4.  Make sure your code lints.
5.  Issue that pull request!
