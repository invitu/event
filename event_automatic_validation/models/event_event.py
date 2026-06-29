# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class EventEvent(models.Model):
    _name = "event.event"
    _inherit = ["event.event", "base.automatic.validation"]

    _automatic_validation_company_field = "company_id"

    automatic_validation_rule_ids = fields.One2many(
        "automatic.validation.rule",
        "event_id",
        string="Validation Rules",
        copy=True,
        compute="_compute_automatic_validation_rule_ids",
        store=True,
        readonly=False,
    )

    @api.depends("event_type_id")
    def _compute_automatic_validation_rule_ids(self):
        """Copy rules from event.type — same pattern as _compute_event_mail_ids."""
        for event in self:
            if not event.event_type_id and not event.automatic_validation_rule_ids:
                continue
            rules_to_remove = event.automatic_validation_rule_ids.filtered(
                lambda r: not r._origin.id
            )
            command = [Command.unlink(r.id) for r in rules_to_remove]
            if event.event_type_id.automatic_validation_rule_ids:
                existing_vals = {
                    frozenset(r._prepare_event_rule_values().items())
                    for r in event.automatic_validation_rule_ids - rules_to_remove
                }
                for rule in event.event_type_id.automatic_validation_rule_ids:
                    vals = rule._prepare_event_rule_values()
                    if frozenset(vals.items()) not in existing_vals:
                        command.append(Command.create(vals))
            if command:
                event.automatic_validation_rule_ids = command

    def _rule_domain(self):
        return [
            ("model", "=", self._name),
            ("event_id", "in", self.ids),
            ("active", "=", True),
            ("company_id", "in", [False] + self._get_company().ids),
        ]

    def _get_validation_trigger_fields(self):
        return ["stage_id"]
