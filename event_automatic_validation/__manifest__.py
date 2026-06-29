# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Event Automatic Validation",
    "version": "18.0.1.0.0",
    "category": "Marketing",
    "author": "INVITU, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/event",
    "license": "AGPL-3",
    "depends": ["base_automatic_validation", "event"],
    "data": [
        "security/ir.model.access.csv",
        "views/automatic_validation_rule_views.xml",
        "views/event_type_views.xml",
        "views/event_event_views.xml",
        "views/event_registration_views.xml",
    ],
    "installable": True,
}
