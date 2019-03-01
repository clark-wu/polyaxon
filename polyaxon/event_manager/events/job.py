from event_manager import event_actions, event_subjects
from event_manager.event import Attribute, Event

JOB_STARTED = '{}.{}'.format(event_subjects.JOB, event_actions.STARTED)
JOB_STARTED_TRIGGERED = '{}.{}.{}'.format(event_subjects.JOB,
                                          event_actions.STARTED,
                                          event_subjects.TRIGGER)
JOB_STOPPED = '{}.{}'.format(event_subjects.JOB, event_actions.STOPPED)
JOB_STOPPED_TRIGGERED = '{}.{}.{}'.format(event_subjects.JOB,
                                          event_actions.STOPPED,
                                          event_subjects.TRIGGER)
JOB_CREATED = '{}.{}'.format(event_subjects.JOB, event_actions.CREATED)
JOB_VIEWED = '{}.{}'.format(event_subjects.JOB, event_actions.VIEWED)
JOB_ARCHIVED = '{}.{}'.format(event_subjects.JOB, event_actions.ARCHIVED)
JOB_RESTORED = '{}.{}'.format(event_subjects.JOB, event_actions.RESTORED)
JOB_BOOKMARKED = '{}.{}'.format(event_subjects.JOB, event_actions.BOOKMARKED)
JOB_UNBOOKMARKED = '{}.{}'.format(event_subjects.JOB, event_actions.UNBOOKMARKED)
JOB_UPDATED = '{}.{}'.format(event_subjects.JOB, event_actions.UPDATED)
JOB_NEW_STATUS = '{}.{}'.format(event_subjects.JOB, event_actions.NEW_STATUS)
JOB_FAILED = '{}.{}'.format(event_subjects.JOB, event_actions.FAILED)
JOB_SUCCEEDED = '{}.{}'.format(event_subjects.JOB, event_actions.SUCCEEDED)
JOB_DONE = '{}.{}'.format(event_subjects.JOB, event_actions.DONE)

JOB_DELETED = '{}.{}'.format(event_subjects.JOB, event_actions.DELETED)
JOB_DELETED_TRIGGERED = '{}.{}.{}'.format(event_subjects.JOB,
                                          event_actions.DELETED,
                                          event_subjects.TRIGGER)
JOB_CLEANED_TRIGGERED = '{}.{}.{}'.format(event_subjects.JOB,
                                          event_actions.CLEANED,
                                          event_subjects.TRIGGER)
JOB_LOGS_VIEWED = '{}.{}'.format(event_subjects.JOB, event_actions.LOGS_VIEWED)
JOB_OUTPUTS_DOWNLOADED = '{}.{}'.format(event_subjects.JOB, event_actions.OUTPUTS_DOWNLOADED)
JOB_RESTARTED_TRIGGERED = '{}.{}.{}'.format(event_subjects.JOB,
                                            event_actions.RESTARTED,
                                            event_subjects.TRIGGER)
JOB_STATUSES_VIEWED = '{}.{}'.format(event_subjects.JOB,
                                     event_actions.STATUSES_VIEWED)
JOB_RESTARTED = '{}.{}'.format(event_subjects.JOB,
                               event_actions.RESTARTED)


class JobCreatedEvent(Event):
    event_type = JOB_CREATED
    actor = True
    actor_id = 'user.id'
    actor_name = 'user.username'
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('created_at', is_datetime=True),
        Attribute('has_specification', attr_type=bool),
        Attribute('has_description', attr_type=bool),
    )


class JobUpdatedEvent(Event):
    event_type = JOB_UPDATED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('created_at', is_datetime=True),
        Attribute('has_description', attr_type=bool),
    )


class JobStartedEvent(Event):
    event_type = JOB_STARTED
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
    )


class JobStartedTriggeredEvent(Event):
    event_type = JOB_STARTED_TRIGGERED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
    )


class JobSoppedEvent(Event):
    event_type = JOB_STOPPED
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('previous_status', is_required=False),
    )


class JobSoppedTriggeredEvent(Event):
    event_type = JOB_STOPPED_TRIGGERED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
    )


class JobViewedEvent(Event):
    event_type = JOB_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('has_description', attr_type=bool),
    )


class JobArchivedEvent(Event):
    event_type = JOB_ARCHIVED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('has_description', attr_type=bool),
    )


class JobRestoredEvent(Event):
    event_type = JOB_RESTORED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('has_description', attr_type=bool),
    )


class JobBookmarkedEvent(Event):
    event_type = JOB_BOOKMARKED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('has_description', attr_type=bool),
    )


class JobUnBookmarkedEvent(Event):
    event_type = JOB_UNBOOKMARKED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('last_status'),
        Attribute('has_description', attr_type=bool),
    )


class JobNewStatusEvent(Event):
    event_type = JOB_NEW_STATUS
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('last_status'),
    )


class JobSucceededEvent(Event):
    event_type = JOB_SUCCEEDED
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('last_status'),
        Attribute('previous_status', is_required=False),
    )


class JobFailedEvent(Event):
    event_type = JOB_FAILED
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('last_status'),
        Attribute('previous_status', is_required=False),
    )


class JobDoneEvent(Event):
    event_type = JOB_DONE
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('last_status'),
        Attribute('previous_status', is_required=False),
    )


class JobDeletedEvent(Event):
    event_type = JOB_DELETED
    attributes = (
        Attribute('id'),
    )


class JobDeletedTriggeredEvent(Event):
    event_type = JOB_DELETED_TRIGGERED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('has_description', attr_type=bool),
        Attribute('last_status'),
    )


class JobCleanedTriggeredEvent(Event):
    event_type = JOB_CLEANED_TRIGGERED
    attributes = (
        Attribute('id'),
    )


class JobLogsViewedEvent(Event):
    event_type = JOB_LOGS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('user.id'),
        Attribute('has_description', attr_type=bool),
        Attribute('last_status'),
    )


class JobOutputsDownloadedEvent(Event):
    event_type = JOB_OUTPUTS_DOWNLOADED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('user.id'),
        Attribute('has_description', attr_type=bool),
        Attribute('last_status'),
    )


class JobRestartedTriggeredEvent(Event):
    event_type = JOB_RESTARTED_TRIGGERED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('user.id'),
        Attribute('has_description', attr_type=bool),
        Attribute('last_status'),
    )


class JobStatusesViewedEvent(Event):
    event_type = JOB_STATUSES_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('user.id'),
        Attribute('last_status'),
    )


class JobRestartedEvent(Event):
    event_type = JOB_RESTARTED
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('user.id'),
        Attribute('has_description', attr_type=bool),
        Attribute('last_status'),
    )
