# pylint:disable=ungrouped-imports
import uuid

import pytest

import activitylogs

from db.models.activitylogs import ActivityLog
from event_manager.events.experiment import EXPERIMENT_DELETED_TRIGGERED
from event_manager.events.user import USER_ACTIVATED
from factories.factory_experiments import ExperimentFactory
from factories.factory_users import UserFactory
from tests.utils import BaseTest


@pytest.mark.activitylogs_mark
class ActivityLogsTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.experiment = ExperimentFactory()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
        self.user = UserFactory()

    def test_record_creates_activities(self):
        assert ActivityLog.objects.count() == 0
        activitylogs.record(ref_id=uuid.uuid4(),
                            event_type=USER_ACTIVATED,
                            instance=self.user,
                            actor_id=self.admin.id,
                            actor_name=self.admin.username)

        assert ActivityLog.objects.count() == 1
        activity = ActivityLog.objects.last()
        assert activity.event_type == USER_ACTIVATED
        assert activity.content_object == self.user
        assert activity.actor == self.admin

        activitylogs.record(ref_id=uuid.uuid4(),
                            event_type=EXPERIMENT_DELETED_TRIGGERED,
                            instance=self.experiment,
                            actor_id=self.admin.id,
                            actor_name=self.admin.username)

        assert ActivityLog.objects.count() == 2
        activity = ActivityLog.objects.last()
        assert activity.event_type == EXPERIMENT_DELETED_TRIGGERED
        assert activity.content_object == self.experiment
        assert activity.actor == self.admin
