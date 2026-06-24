import unittest
import time
from guardian_bot import redact_pii, fetch_safety_protocol


class TestGuardianSecurityAndLogic(unittest.TestCase):

    def setUp(self):
        """Set up standard text fragments for regression testing execution."""
        print(f"\n🚀 Initializing: {self._testMethodName}")
        self.start_time = time.time()

    def tearDown(self):
        """Calculate execution performance constraints post-test."""
        duration = (time.time() - self.start_time) * 1000
        print(f"⏱️ Operational Latency: {duration:.2f} ms")

    def test_pii_redaction_ssn_variations(self):
        """STRESS TEST 1: Verify SSN variations are cleanly scrubbed by the Regex Pipeline."""
        test_cases = [
            "My social is 000-12-3456 code.",
            "Account opened with 000.12.3456 details.",
            "Check registration number 000 12 3456 immediately.",
            "Raw format verification: 000123456."
        ]

        for case in test_cases:
            sanitized = redact_pii(case)
            self.assertIn("[🔒 SSN REDACTED]", sanitized)
            self.assertNotIn("000-12-3456", sanitized)
            self.assertNotIn("000123456", sanitized)

    def test_pii_redaction_phone_variations(self):
        """STRESS TEST 2: Verify telephone variations are masked locally at the edge."""
        test_cases = [
            "Call me back at 305-555-1234.",
            "Dialing contact number +1 (305) 555-1234 now.",
            "Reach out via 305.555.1234 text stream.",
            "Direct array format 3055551234 hook."
        ]

        for case in test_cases:
            sanitized = redact_pii(case)
            self.assertIn("[🔒 PHONE REDACTED]", sanitized)
            self.assertNotIn("305-555-1234", sanitized)
            self.assertNotIn("3055551234", sanitized)

    def test_pii_redaction_email_and_cards(self):
        """STRESS TEST 3: Verify email layouts and credit cards are scrubbed simultaneously."""
        complex_text = "Send confirmation to target@gmail.com from card 4111-2222-3333-4444."
        sanitized = redact_pii(complex_text)

        self.assertIn("[🔒 EMAIL REDACTED]", sanitized)
        self.assertIn("[🔒 CREDIT CARD REDACTED]", sanitized)
        self.assertNotIn("target@gmail.com", sanitized)
        self.assertNotIn("4111-2222-3333-4444", sanitized)

    def test_failover_keyword_routing(self):
        """LOGIC TEST 4: Verify the local failover engine correctly routes targeted safety protocols."""
        # Test Grandparent Scam keyword mapping
        grandparent_hint = "They claim my grandson is in jail and needs bail money!"
        protocol_1 = fetch_safety_protocol(grandparent_hint)
        self.assertIn("grandparent scam", protocol_1.lower())

        # Test Phishing link mapping
        phishing_hint = "Click this secure link to unlock your bank account online."
        protocol_2 = fetch_safety_protocol(phishing_hint)
        self.assertIn("phishing", protocol_2.lower())


if __name__ == "__main__":
    print("🛡️ Commencing Guardian Automated Quality Assurance Regression Suite...")
    unittest.main()