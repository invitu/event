# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AutomaticValidationRule(models.Model):
    _inherit = "automatic.validation.rule"
    _name = "automatic.validation.rule"

    model = fields.Selection(
        selection_add=[
            ("event.event", "Event"),
            ("event.registration", "Registration"),
        ],
        ondelete={
            "event.event": "cascade",
            "event.registration": "cascade",
        },
    )
    event_type_id = fields.Many2one(
        "event.type",
        ondelete="cascade",
        index=True,
    )
    event_id = fields.Many2one(
        "event.event",
        ondelete="cascade",
        index=True,
    )

    def _prepare_event_rule_values(self):
        self.ensure_one()
        return {
            "name": self.name,
            "model": self.model,
            "sequence": self.sequence,
            "check_type": self.check_type,
            "domain": self.domain,
            "code": self.code,
            "company_id": self.company_id.id,
        }
