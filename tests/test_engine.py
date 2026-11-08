import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

from core.engine import slugify, DeepResearchEngine

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slugify(self):
        self.assertEqual(slugify("Speculative Tool Calling & Typed Decision Layers"), "speculative-tool-calling-typed-decision-layers")
        self.assertEqual(slugify("KV-Cache: Prefix Pinning vs Eviction!"), "kv-cache-prefix-pinning-vs-eviction")
        self.assertEqual(slugify("   Leading & Trailing Spaces   "), "leading-trailing-spaces")
        self.assertEqual(slugify(""), "")

    def test_engine_init_mock_client(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(model_name="gemini-2.5-flash", client=mock_client)
        self.assertEqual(engine.model_name, "gemini-2.5-flash")
        self.assertEqual(engine.client, mock_client)

    def test_decompose_topic_fallback(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(client=mock_client)
        engine._call_gemini_with_retry = MagicMock(side_effect=Exception("API Error"))

        vectors = engine.decompose_topic("Autonomous Systems")
        self.assertEqual(len(vectors), 4)
        self.assertIn("Foundational Architecture & Mathematical Formulation", vectors)

    def test_decompose_topic_success(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(client=mock_client)
        engine._call_gemini_with_retry = MagicMock(
            return_value='["Vector 1", "Vector 2", "Vector 3", "Vector 4"]'
        )

        vectors = engine.decompose_topic("Distributed Consensus")
        self.assertEqual(vectors, ["Vector 1", "Vector 2", "Vector 3", "Vector 4"])

    def test_investigate_vector(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(client=mock_client)
        engine._call_gemini_with_retry = MagicMock(return_value="Detailed findings on consensus.")

        with patch("time.sleep", return_value=None):
            result = engine.investigate_vector("Consensus", "Raft vs Paxos")
        self.assertEqual(result, "Detailed findings on consensus.")
        engine._call_gemini_with_retry.assert_called_once()

    def test_synthesize_whitepaper(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(client=mock_client)
        engine._call_gemini_with_retry = MagicMock(return_value="# Production Architecture\n\nExecutive Abstract here.")

        whitepaper = engine.synthesize_whitepaper(
            "Vector DB Sharding",
            ["Vector 1", "Vector 2"],
            ["Finding 1", "Finding 2"]
        )
        self.assertIn("# Production Architecture", whitepaper)

    def test_run_pipeline_e2e_mocked(self):
        mock_client = MagicMock()
        engine = DeepResearchEngine(client=mock_client)
        engine.decompose_topic = MagicMock(return_value=["V1", "V2"])
        engine.investigate_vector = MagicMock(return_value="Technical vector evaluation.")
        engine.synthesize_whitepaper = MagicMock(return_value="# Title\n\nExecutive Abstract.")

        with patch("core.engine.REPORTS_DIR", self.temp_dir), \
             patch("core.engine.send_telegram", return_value=True):
            report_file = engine.run("Test E2E Topic")

            self.assertTrue(report_file.exists())
            content = report_file.read_text(encoding="utf-8")
            self.assertIn("# Title", content)
            self.assertIn("test-e2e-topic.md", report_file.name)

if __name__ == "__main__":
    unittest.main()
