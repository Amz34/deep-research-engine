import unittest
from unittest.mock import MagicMock, patch
from core.trending_detector import AI_SYSTEMS_KEYWORDS, detect_trending_theme

class TestTrendingDetector(unittest.TestCase):
    def test_keywords_defined(self):
        self.assertIn("llm", AI_SYSTEMS_KEYWORDS)
        self.assertIn("agent", AI_SYSTEMS_KEYWORDS)
        self.assertIn("inference", AI_SYSTEMS_KEYWORDS)
        self.assertIn("kv-cache", AI_SYSTEMS_KEYWORDS)
        self.assertGreater(len(AI_SYSTEMS_KEYWORDS), 10)

    @patch("core.trending_detector.fetch_hn_top_stories")
    @patch("core.trending_detector.fetch_arxiv_recent")
    def test_detect_trending_theme_generation(self, mock_arxiv, mock_hn):
        mock_hn.return_value = [{"title": "Show HN: Fast KV-Cache engine", "score": 250, "url": "http://hn.test"}]
        mock_arxiv.return_value = ["Speculative Decoding with Quantized Verifiers"]

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Distributed KV-Cache Compression for Sovereign Agent Swarms"
        mock_client.models.generate_content.return_value = mock_response

        with patch.dict("sys.modules", {"google.genai": MagicMock(), "google.genai.types": MagicMock()}):
            theme = detect_trending_theme(mock_client, existing_slugs=["some-old-topic"])

        self.assertEqual(theme, "Distributed KV-Cache Compression for Sovereign Agent Swarms")
        mock_client.models.generate_content.assert_called_once()

if __name__ == "__main__":
    unittest.main()
