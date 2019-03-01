from event_manager import event_actions, event_subjects
from event_manager.event import Attribute, Event

EXPERIMENT_JOB_VIEWED = '{}.{}'.format(event_subjects.EXPERIMENT_JOB,
                                       event_actions.VIEWED)
EXPERIMENT_JOB_NEW_STATUS = '{}.{}'.format(event_subjects.EXPERIMENT_JOB, event_actions.NEW_STATUS)
EXPERIMENT_JOB_RESOURCES_VIEWED = '{}.{}'.format(event_subjects.EXPERIMENT_JOB,
                                                 event_actions.RESOURCES_VIEWED)
EXPERIMENT_JOB_LOGS_VIEWED = '{}.{}'.format(event_subjects.EXPERIMENT_JOB,
                                            event_actions.LOGS_VIEWED)
EXPERIMENT_JOB_STATUSES_VIEWED = '{}.{}'.format(event_subjects.EXPERIMENT_JOB,
                                                event_actions.STATUSES_VIEWED)


class ExperimentJobViewedEvent(Event):
    event_type = EXPERIMENT_JOB_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('role'),
        Attribute('experiment.id'),
        Attribute('experiment.user.id'),
        Attribute('last_status'),
    )


class ExperimentJobResourcesViewedEvent(Event):
    event_type = EXPERIMENT_JOB_RESOURCES_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('experiment.id'),
        Attribute('experiment.user.id'),
        Attribute('last_status'),
    )


class ExperimentJobLogsViewedEvent(Event):
    event_type = EXPERIMENT_JOB_LOGS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('experiment.id'),
        Attribute('experiment.user.id'),
        Attribute('last_status'),
    )


class ExperimentJobStatusesViewedEvent(Event):
    event_type = EXPERIMENT_JOB_STATUSES_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('experiment.id'),
        Attribute('experiment.user.id'),
        Attribute('last_status'),
    )


class ExperimentJobNewStatusEvent(Event):
    event_type = EXPERIMENT_JOB_NEW_STATUS
    attributes = (
        Attribute('id'),
    )
