from event_manager import event_actions, event_subjects
from event_manager.event import Attribute, Event

PROJECT_CREATED = '{}.{}'.format(event_subjects.PROJECT, event_actions.CREATED)
PROJECT_UPDATED = '{}.{}'.format(event_subjects.PROJECT, event_actions.UPDATED)
PROJECT_DELETED = '{}.{}'.format(event_subjects.PROJECT, event_actions.DELETED)
PROJECT_DELETED_TRIGGERED = '{}.{}.{}'.format(event_subjects.PROJECT,
                                              event_actions.DELETED,
                                              event_subjects.TRIGGER)
PROJECT_VIEWED = '{}.{}'.format(event_subjects.PROJECT, event_actions.VIEWED)
PROJECT_ARCHIVED = '{}.{}'.format(event_subjects.PROJECT, event_actions.ARCHIVED)
PROJECT_RESTORED = '{}.{}'.format(event_subjects.PROJECT, event_actions.RESTORED)
PROJECT_BOOKMARKED = '{}.{}'.format(event_subjects.PROJECT, event_actions.BOOKMARKED)
PROJECT_UNBOOKMARKED = '{}.{}'.format(event_subjects.PROJECT, event_actions.UNBOOKMARKED)
PROJECT_SET_PUBLIC = '{}.set_public'.format(event_subjects.PROJECT)  # Not set
PROJECT_SET_PRIVATE = '{}.set_private'.format(event_subjects.PROJECT)  # Not set
PROJECT_EXPERIMENTS_VIEWED = '{}.{}'.format(event_subjects.PROJECT,
                                            event_actions.EXPERIMENTS_VIEWED)
PROJECT_JOBS_VIEWED = '{}.{}'.format(event_subjects.PROJECT,
                                     event_actions.JOBS_VIEWED)
PROJECT_BUILDS_VIEWED = '{}.{}'.format(event_subjects.PROJECT,
                                       event_actions.BUILDS_VIEWED)
PROJECT_TENSORBOARDS_VIEWED = '{}.{}'.format(event_subjects.PROJECT,
                                             event_actions.TENSORBOARDS_VIEWED)
PROJECT_EXPERIMENT_GROUPS_VIEWED = '{}.{}'.format(event_subjects.PROJECT,
                                                  event_actions.EXPERIMENT_GROUPS_VIEWED)


class ProjectCreatedEvent(Event):
    event_type = PROJECT_CREATED
    actor = True
    actor_id = 'user.id'
    actor_name = 'user.username'
    attributes = (
        Attribute('id'),
        Attribute('created_at', is_datetime=True),
        Attribute('has_description', attr_type=bool),
        Attribute('is_public', attr_type=bool),
    )


class ProjectUpdatedEvent(Event):
    event_type = PROJECT_UPDATED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('updated_at', is_datetime=True),
        Attribute('has_description', attr_type=bool),
        Attribute('is_public', attr_type=bool),
    )


class ProjectDeletedEvent(Event):
    event_type = PROJECT_DELETED
    attributes = (
        Attribute('id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectDeletedTriggeredEvent(Event):
    event_type = PROJECT_DELETED_TRIGGERED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectViewedEvent(Event):
    event_type = PROJECT_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectArchivedEvent(Event):
    event_type = PROJECT_ARCHIVED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectRestoredEvent(Event):
    event_type = PROJECT_RESTORED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectBookmarkedEvent(Event):
    event_type = PROJECT_BOOKMARKED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectUnBookmarkedEvent(Event):
    event_type = PROJECT_UNBOOKMARKED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectSetPublicEvent(Event):
    event_type = PROJECT_SET_PUBLIC
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
    )


class ProjectSetPrivateEvent(Event):
    event_type = PROJECT_SET_PRIVATE
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
    )


class ProjectExperimentsViewedEvent(Event):
    event_type = PROJECT_EXPERIMENTS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectJobsViewedEvent(Event):
    event_type = PROJECT_JOBS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectBuildsViewedEvent(Event):
    event_type = PROJECT_BUILDS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectTensorboardsViewedEvent(Event):
    event_type = PROJECT_TENSORBOARDS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )


class ProjectExperimentGroupsViewedEvent(Event):
    event_type = PROJECT_EXPERIMENT_GROUPS_VIEWED
    actor = True
    attributes = (
        Attribute('id'),
        Attribute('user.id'),
        Attribute('is_public', attr_type=bool),
    )
