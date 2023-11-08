from celery import shared_task



@shared_task()
def find_participants_dublicates(cycle_id):
    from future_ticket.models import StudentBVB, EventsCycle

    cycle = EventsCycle.objects.get(id=cycle_id)
    events = cycle.events.all().order_by('event_date')
    for event in events:
        for participant in event.participants.all():
            dublicates = StudentBVB.objects.filter(bvb_id=participant.bvb_id)
            if len(dublicates) > 1:
                dublicates.order_by('-event__event_date').update(
                    is_double=True
                )
            original = dublicates.first()
            original.is_double=False
            original.save()

@shared_task()
def update_completed_quota():
    from future_ticket.models import TicketQuota, QuotaEvent, StudentBVB
    quotas = []
    for quota in TicketQuota.objects.exclude(approved_value=0):
        quota_events = QuotaEvent.objects.filter(quota=quota)
        completed_quota = 0
        for quota_event in quota_events:
            event=quota_event.event
            participants = StudentBVB.objects.filter(
                school=quota.school, event=event, is_attend=True, is_double=False).count()
            if participants > quota_event.reserved_quota:
                participants = quota_event.reserved_quota
            completed_quota += participants
        quota.completed_quota = completed_quota
        quotas.append(quota)
    TicketQuota.objects.bulk_update(quotas, ['completed_quota'])