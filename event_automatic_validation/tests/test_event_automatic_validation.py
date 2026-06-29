# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.tests.common import TransactionCase


class TestEventAutomaticValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event_type = cls.env["event.type"].create({"name": "Test Type"})
        cls.event = cls.env["event.event"].create(
            {
                "name": "Test Event",
                "date_begin": datetime(2026, 9, 1, 8, 0),
                "date_end": datetime(2026, 9, 1, 18, 0),
                "event_type_id": cls.event_type.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        cls.registration = cls.env["event.registration"].create(
            {
                "event_id": cls.event.id,
                "name": "Test Attendee",
            }
        )

    def _make_rule(self, model, domain=None, code=None, event_id=None):
        return self.env["automatic.validation.rule"].create(
            {
                "name": "Test Rule",
                "model": model,
                "check_type": "by_domain" if domain else "by_py_code",
                "domain": domain or "[]",
                "code": code,
                "event_id": event_id,
            }
        )

    def test_registration_complete(self):
        """detect_incomplete_rules sets complete when all rules pass."""
        rule = self._make_rule(
            "event.registration",
            domain="[('name', '!=', False)]",
            event_id=self.event.id,
        )
        self.registration.detect_incomplete_rules()
        self.assertEqual(self.registration.validation_status, "complete")
        self.assertNotIn(rule, self.registration.incomplete_rule_ids)
        rule.unlink()

    def test_registration_incomplete(self):
        """detect_incomplete_rules adds failing rule to incomplete_rule_ids."""
        rule = self._make_rule(
            "event.registration",
            domain="[('attendee_partner_id', '!=', False)]",
            event_id=self.event.id,
        )
        self.registration.detect_incomplete_rules()
        self.assertIn(rule, self.registration.incomplete_rule_ids)
        self.assertEqual(self.registration.validation_status, "incomplete")
        rule.unlink()

    def test_registration_rule_skipped_for_other_event(self):
        """Rule from another event is not applied to this registration."""
        other_event = self.env["event.event"].create(
            {
                "name": "Other Event",
                "date_begin": datetime(2026, 10, 1, 8, 0),
                "date_end": datetime(2026, 10, 1, 18, 0),
            }
        )
        rule = self._make_rule(
            "event.registration",
            domain="[('attendee_partner_id', '!=', False)]",
            event_id=other_event.id,
        )
        self.registration.detect_incomplete_rules()
        self.assertNotIn(rule, self.registration.incomplete_rule_ids)
        rule.unlink()
        other_event.unlink()

    def test_registration_write_triggers_check(self):
        """Writing attendee_partner_id triggers detect_incomplete_rules."""
        rule = self._make_rule(
            "event.registration",
            domain="[('attendee_partner_id', '!=', False)]",
            event_id=self.event.id,
        )
        self.assertIn(rule, self.registration.incomplete_rule_ids)
        self.registration.write({"attendee_partner_id": self.partner.id})
        self.assertNotIn(rule, self.registration.incomplete_rule_ids)
        rule.unlink()

    def test_event_complete(self):
        """detect_incomplete_rules on event sets complete when rules pass."""
        rule = self._make_rule(
            "event.event",
            domain="[('name', '!=', False)]",
            event_id=self.event.id,
        )
        self.event.detect_incomplete_rules()
        self.assertEqual(self.event.validation_status, "complete")
        self.assertNotIn(rule, self.event.incomplete_rule_ids)
        rule.unlink()

    def test_event_incomplete(self):
        """detect_incomplete_rules on event sets incomplete when rule fails."""
        rule = self._make_rule(
            "event.event",
            domain="[('id', '=', 0)]",
            event_id=self.event.id,
        )
        self.event.detect_incomplete_rules()
        self.assertIn(rule, self.event.incomplete_rule_ids)
        self.assertEqual(self.event.validation_status, "incomplete")
        rule.unlink()

    def test_rules_copied_from_event_type(self):
        """Rules from event.type are copied to event.event on creation."""
        rule = self.env["automatic.validation.rule"].create(
            {
                "name": "Type Rule",
                "model": "event.registration",
                "check_type": "by_domain",
                "domain": "[('name', '!=', False)]",
                "event_type_id": self.event_type.id,
            }
        )
        new_event = self.env["event.event"].create(
            {
                "name": "New Event",
                "date_begin": datetime(2026, 11, 1, 8, 0),
                "date_end": datetime(2026, 11, 1, 18, 0),
                "event_type_id": self.event_type.id,
            }
        )
        self.assertTrue(new_event.automatic_validation_rule_ids)
        rule.unlink()
        new_event.unlink()

    def test_rules_updated_on_type_change(self):
        """Rules are updated when event_type_id changes."""
        new_type = self.env["event.type"].create({"name": "New Type"})
        rule = self.env["automatic.validation.rule"].create(
            {
                "name": "New Type Rule",
                "model": "event.registration",
                "check_type": "by_domain",
                "domain": "[('name', '!=', False)]",
                "event_type_id": new_type.id,
            }
        )
        self.event.event_type_id = new_type
        self.assertTrue(
            any(
                r.name == "New Type Rule"
                for r in self.event.automatic_validation_rule_ids
            )
        )
        rule.unlink()
        new_type.unlink()
