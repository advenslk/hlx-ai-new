"""
HELZERX AI Support - Ticket Formatting & Lifecycle Tests
Tests ticket ID generation, slug sanitization, and HTML transcript generation.
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.utils.helpers import generate_ticket_id, sanitize_channel_name
from bot.tickets.transcript import generate_html_transcript


class TestTicketSystem(unittest.TestCase):

    def test_ticket_id_generation(self):
        """Verify ticket ID format."""
        tid = generate_ticket_id("HZX")
        self.assertTrue(tid.startswith("HZX-"))
        self.assertEqual(len(tid), 8) # e.g. HZX-1234
        self.assertTrue(tid.split("-")[1].isdigit())

    def test_sanitize_channel_name(self):
        """Verify channel slug generation prevents illegal Discord characters."""
        chan = sanitize_channel_name(
            ticket_id="HZX-8429",
            category="minecraft",
            username="User!@#_Test"
        )
        self.assertIn("hzx-8429", chan)
        self.assertIn("minecraf", chan)
        # Should not contain spaces or uppercase
        self.assertNotIn(" ", chan)
        self.assertEqual(chan, chan.lower())

    def test_html_transcript_generation(self):
        """Verify complete HTML transcript file creation and formatting."""
        messages = [
            {
                "author_name": "TestCustomer",
                "author_role": "customer",
                "content": "Server is reporting out of memory error.",
                "created_at": "12:00:00 UTC"
            },
            {
                "author_name": "HELZERX AI Support",
                "author_role": "ai",
                "content": "Please inspect your -Xmx JVM startup flags.",
                "created_at": "12:00:02 UTC"
            },
            {
                "author_name": "SupportLead",
                "author_role": "staff",
                "content": "Increased container limit by 1GB. Issue resolved.",
                "created_at": "12:05:00 UTC"
            }
        ]

        html_out, file_path = generate_html_transcript(
            ticket_code="HZX-1042",
            customer_name="TestCustomer",
            category="Minecraft Hosting",
            priority="HIGH",
            status="CLOSED",
            messages=messages
        )

        self.assertIn("HZX-1042", html_out)
        self.assertIn("TestCustomer", html_out)
        self.assertIn("Increased container limit", html_out)
        self.assertIn("HELZERX AI", html_out)
        self.assertTrue(file_path.exists())


if __name__ == "__main__":
    unittest.main()
