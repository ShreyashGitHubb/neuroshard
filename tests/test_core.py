import unittest
import os
import shutil
import json
from shard.core.chunker import chunk_file, decompress_chunk
from shard.core.store import LocalStore
from shard.core.manifest import create_manifest

class TestCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_env"
        os.makedirs(self.test_dir, exist_ok=True)
        self.store = LocalStore(root_dir=os.path.join(self.test_dir, ".shard"))
        self.store.init()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_chunking_and_reconstruction(self):
        # Create random file
        data = os.urandom(5 * 1024 * 1024) # 5MB
        file_path = os.path.join(self.test_dir, "data.bin")
        with open(file_path, "wb") as f:
            f.write(data)

        # Chunk
        blocks = chunk_file(file_path)
        self.assertTrue(len(blocks) > 1) # Should be at least 2 chunks (4MB + 1MB)

        # Store
        for block in blocks:
            self.store.write_object(block["hash"], block["data"])

        # Reconstruct
        reconstructed = b""
        for block in blocks:
            compressed = self.store.read_object(block["hash"])
            reconstructed += decompress_chunk(compressed)

        self.assertEqual(data, reconstructed)

    def test_manifest_creation(self):
        blocks = [{"hash": "abc", "size": 123, "data": b"x"}]
        mhash, manifest, _ = create_manifest("foo.bin", blocks, {"msg": "hi"})
        self.assertEqual(manifest["file_path"], "foo.bin")
        self.assertEqual(manifest["meta"]["msg"], "hi")
        self.assertEqual(len(manifest["blocks"]), 1)
        # Ensure 'data' is not in manifest blocks
        self.assertNotIn("data", manifest["blocks"][0])

if __name__ == "__main__":
    unittest.main()
