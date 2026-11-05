"""
HELZERX AI Support - AI Engine & Multi-Language Tests
Tests language detection (English, Sinhala, Singlish), classifier, prompt builder, and AI fallback.
"""
import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.ai.language_detector import detect_language
from bot.ai.classifier import classify_ticket
from bot.ai.prompts import build_ticket_ai_prompt
from bot.ai.client import NvidiaNimClient


class TestAIEngine(unittest.TestCase):

    def test_language_detection_english(self):
        """Verify English detection."""
        text = "Hello support, my Minecraft server stopped responding and I need help configuring Aikar flags."
        lang, conf = detect_language(text)
        self.assertEqual(lang, "en")
        self.assertGreaterEqual(conf, 0.7)

    def test_language_detection_sinhala(self):
        """Verify Sinhala Unicode script detection."""
        text = "මගේ සර්වර් එකේ ප්ලගින් එකක් වැඩ කරන්නේ නැහැ. කරුණාකරලා උදව් කරන්න."
        lang, conf = detect_language(text)
        self.assertEqual(lang, "si")
        self.assertGreaterEqual(conf, 0.8)

    def test_language_detection_singlish(self):
        """Verify Singlish detection."""
        samples = [
            "mage server eka start wenne na bro help ekak puluwanda",
            "pterodactyl wings offline wela thiyenne balanna",
            "ape server eke lag wenawa kohomada hadaganne"
        ]
        for s in samples:
            lang, conf = detect_language(s)
            self.assertEqual(lang, "singlish", f"Failed Singlish detection on '{s}' (got {lang})")

    def test_smart_ticket_classification_urgent(self):
        """Verify mission-critical issues receive URGENT priority."""
        res = classify_ticket(
            subject="Production node offline and crashed",
            description="Entire dedicated server is down under DDoS attack",
            category_hint="dedicated"
        )
        self.assertEqual(res.priority, "URGENT")
        self.assertEqual(res.category, "dedicated")

    def test_smart_ticket_classification_minecraft(self):
        """Verify Minecraft intent mapping."""
        res = classify_ticket(
            subject="Paper 1.20 server won't start",
            description="Error in console: Could not load plugin EssentialsX",
            category_hint="general" # Will be reclassified
        )
        self.assertEqual(res.category, "minecraft")
        self.assertEqual(res.department, "Game Server Operations")

    def test_human_escalation_detection(self):
        """Verify human escalation trigger."""
        res = classify_ticket(
            subject="Need to talk to human support",
            description="Can I speak to a real representative or staff please?",
            category_hint="general"
        )
        self.assertTrue(res.is_human_escalation_needed)

    def test_ai_prompt_generation(self):
        """Verify prompt contains safety directives and metadata."""
        prompt = build_ticket_ai_prompt(
            ticket_code="HZX-9021",
            category="VPS Support",
            priority="HIGH",
            customer_name="Kasun",
            initial_subject="UFW blocked SSH",
            initial_description="Locked out of port 22",
            server_identifier="192.168.1.100",
            retrieved_knowledge="Verified doc: Use VNC rescue mode",
            detected_language="singlish"
        )
        self.assertIn("HZX-9021", prompt)
        self.assertIn("Kasun", prompt)
        self.assertIn("Verified doc: Use VNC rescue mode", prompt)
        self.assertIn("NEVER fabricate server diagnostics", prompt)

    def test_nvidia_client_fallback_when_unconfigured(self):
        """Verify graceful diagnostic fallback when API key is unconfigured."""
        client = NvidiaNimClient()
        client.api_key = "" # Empty
        self.assertFalse(client.is_configured())

        async def run_test():
            reply, p_tok, c_tok = await client.generate_response([{"role": "user", "content": "Hi"}])
            self.assertIn("HELZERX AI Diagnostic", reply)
            self.assertGreater(p_tok, 0)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
