"""
HELZERX AI Support - Knowledge Base & RAG Tests
Tests document chunking, relevance scoring, and verified document retrieval.
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.knowledge.rag_engine import chunk_document, score_chunk_relevance, DocumentChunk, RAGEngine
from bot.knowledge.manager import knowledge_manager


class TestKnowledgeBase(unittest.TestCase):

    def test_document_chunking(self):
        """Verify markdown document is partitioned into semantic chunks."""
        text = "Paragraph 1 is about Minecraft Paper JVM flags.\n\nParagraph 2 is about memory limits."
        chunks = chunk_document(title="Minecraft Guide", category="minecraft", full_text=text, max_chunk_words=10)
        self.assertGreaterEqual(len(chunks), 1)
        self.assertEqual(chunks[0].title, "Minecraft Guide")
        self.assertEqual(chunks[0].category, "minecraft")

    def test_relevance_scoring(self):
        """Verify keyword matching accurately scores relevant chunks."""
        chunk = DocumentChunk(
            title="Pterodactyl Wings Troubleshooting",
            category="technical",
            content="When wings daemon fails with EHOSTUNREACH check port 8080 and systemctl status wings."
        )
        score_high = score_chunk_relevance("wings EHOSTUNREACH error", chunk)
        score_low = score_chunk_relevance("billing payment refund", chunk)

        self.assertGreater(score_high, score_low)
        self.assertGreater(score_high, 5.0)

    def test_knowledge_manager_search(self):
        """Verify knowledge manager retrieves verified HELZERX articles."""
        # Query for Minecraft flags
        mc_result = knowledge_manager.search("how to tune Aikar flags for paper server")
        self.assertIn("Aikar", mc_result)
        self.assertIn("Minecraft", mc_result)

        # Query for Cloudflare SRV
        cf_result = knowledge_manager.search("cloudflare srv record orange cloud grey cloud")
        self.assertIn("Cloudflare", cf_result)
        self.assertIn("Grey Cloud", cf_result)


if __name__ == "__main__":
    unittest.main()
