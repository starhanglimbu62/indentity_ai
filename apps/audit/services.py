from apps.audit.models import AuditEvent


class AuditService:
    @staticmethod
    def record_event(user=None, event_type=None, entity_type="", entity_id=None, metadata=None):
        if not event_type:
            raise ValueError("event_type is required.")

        return AuditEvent.objects.create(
            user=user,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )
