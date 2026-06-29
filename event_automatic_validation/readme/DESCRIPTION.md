Applies automatic validation rules to ``event.event`` and
``event.registration`` using the ``base_automatic_validation`` mixin.

Rules are defined on ``event.type`` and automatically copied to each
``event.event`` when the type is selected — the same pattern as
communications and tickets.

**Two independent validation levels**

*Registration level* — rules applied to each attendee:

```
Model: event.registration
Domain: [('attendee_partner_id.phone', '!=', False)]
```

*Event level* — rules applied to the event itself, including rules
that aggregate registration statuses:

```python
# All registrations must be complete before the event starts
result = all(
    r.validation_status == 'complete'
    for r in record.registration_ids
)
```

**Bottom-up propagation**

When a registration is re-evaluated, its parent event is automatically
re-evaluated too. This ensures that event-level rules depending on
registration statuses are always up to date.

**By Method example**

Declare a method on ``event.registration`` and expose it via
``selection_add``:

```python
class AutomaticValidationRule(models.Model):
    _inherit = "automatic.validation.rule"
    _name = "automatic.validation.rule"

    method = fields.Selection(
        selection_add=[
            ("check_has_partner", "Has attendee partner"),
        ],
        ondelete={"check_has_partner": "cascade"},
    )

class EventRegistration(models.Model):
    _inherit = "event.registration"

    def check_has_partner(self):
        return self.filtered(lambda r: not r.attendee_partner_id)
```
