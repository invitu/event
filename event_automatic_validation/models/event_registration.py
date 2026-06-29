# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class EventRegistration(models.Model):
    _name = "event.registration"
    _inherit = ["event.registration", "base.automatic.validation"]

    def _rule_domain(self):
        event_ids = self.mapped("event_id").ids
        return [
            ("model", "=", self._name),
            ("event_id", "in", event_ids),
            ("active", "=", True),
            ("company_id", "in", [False] + self._get_company().ids),
        ]

    def _get_company(self):
        if self and self.event_id.company_id:
            return self.event_id.company_id
        return self.env.company

    def _check_rule(self, rule_info):
        """Skip rule if it belongs to a different event."""
        result = self.env["event.registration"]
        for rec in self:
            rule = self.env["automatic.validation.rule"].browse(rule_info.id)
            if rule.event_id and rule.event_id != rec.event_id:
                continue
            if rule_info.check_type == "by_py_code":
                failing = rec._check_rule_by_py_code(rule_info)
            elif rule_info.check_type == "by_domain":
                failing = rec._check_rule_by_domain(rule_info)
            else:
                failing = self.browse()
            result |= failing
        return result

    def detect_incomplete_rules(self):
        """Evaluate rules and propagate to parent events."""
        result = super().detect_incomplete_rules()
        # Bottom-up propagation: re-evaluate event rules that may depend
        # on registration statuses (e.g. by_py_code checking registration_ids)
        self.mapped("event_id").detect_incomplete_rules()
        return result

    @api.model
    def _get_validation_trigger_fields(self):
        return ["attendee_partner_id", "state"]
