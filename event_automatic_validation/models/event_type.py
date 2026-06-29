# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    automatic_validation_rule_ids = fields.One2many(
        "automatic.validation.rule",
        "event_type_id",
        string="Validation Rules",
        copy=True,
    )
