from adminpanel.models import EventType, MatchEvent

# Create EventType records for any distinct event strings found in MatchEvent.event_type
existing = set(EventType.objects.values_list('name', flat=True))
distinct = set(MatchEvent.objects.exclude(event_type__isnull=True).exclude(event_type='').values_list('event_type', flat=True))
new = distinct - existing
for name in sorted(new):
	EventType.objects.create(name=name)
print(f'Created {len(new)} EventType(s)')