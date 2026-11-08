import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ontology_defined(self):
        import deep_research
        self.assertGreaterEqual(len(deep_research.TRENDING_ONTOLOGY), 5)
        for item in deep_research.TRENDING_ONTOLOGY:
            self.assertIsInstance(item, str)
            self.assertGreater(len(item), 10)

    def test_update_readme_index(self):
        import deep_research

        reports_dir = self.temp_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / "2026-11-08-sample-research-dossier.md"
        report_file.write_text("# Sample Research Dossier Title\n\nExecutive Abstract here.", encoding="utf-8")

        mock_readme = self.temp_dir / "README.md"
        mock_readme.write_text(
            "## 📂 Research Whitepaper Library\n\n| Date | Whitepaper Title | Access Link |\n|:---:|:---|:---:|\n\n---\n",
            encoding="utf-8"
        )

        with patch("deep_research.REPORTS_DIR", reports_dir), \
             patch("deep_research.REPO_DIR", self.temp_dir):
            deep_research.update_readme_index()

        updated_content = mock_readme.read_text(encoding="utf-8")
        self.assertIn("2026-11-08", updated_content)
        self.assertIn("sample-research-dossier.md", updated_content)

    def test_assets_exist(self):
        repo_root = Path(__file__).resolve().parent.parent
        assets_dir = repo_root / "assets"
        self.assertTrue(assets_dir.exists())
        self.assertTrue((assets_dir / "deep-research-overview.jpg").exists())
        self.assertTrue((assets_dir / "github-benefits-growth.jpg").exists())

if __name__ == "__main__":
    unittest.main()
