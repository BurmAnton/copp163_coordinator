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