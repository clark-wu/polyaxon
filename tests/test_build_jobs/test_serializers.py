from unittest.mock import patch

import pytest

from api.build_jobs import queries
from api.build_jobs.serializers import (
    BookmarkedBuildJobSerializer,
    BuildJobDetailSerializer,
    BuildJobSerializer,
    BuildJobStatusSerializer
)
from constants.jobs import JobLifeCycle
from db.models.build_jobs import BuildJob, BuildJobStatus
from db.models.experiments import Experiment
from db.models.jobs import Job
from factories.factory_build_jobs import BuildJobFactory, BuildJobStatusFactory
from tests.utils import BaseTest


@pytest.mark.build_jobs_mark
class TestBuildJobSerializer(BaseTest):
    serializer_class = BuildJobSerializer
    model_class = BuildJob
    factory_class = BuildJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'user',
        'unique_name',
        'pod_id',
        'description',
        'created_at',
        'updated_at',
        'last_status',
        'started_at',
        'finished_at',
        'tags',
        'backend',
        'project',
    }

    def setUp(self):
        super().setUp()
        self.obj1 = self.factory_class()
        self.obj2 = self.factory_class()

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class()
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        BuildJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        BuildJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        data = self.serializer_class(obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.build_jobs_mark
class TestBookmarkedBuildJobSerializer(TestBuildJobSerializer):
    serializer_class = BookmarkedBuildJobSerializer
    expected_keys = TestBuildJobSerializer.expected_keys | {'bookmarked', }

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        assert data.pop('bookmarked') is False
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v


@pytest.mark.build_jobs_mark
class TestBuildJobDetailSerializer(BaseTest):
    serializer_class = BuildJobDetailSerializer
    model_class = BuildJob
    factory_class = BuildJobFactory
    expected_keys = {
        'id',
        'uuid',
        'name',
        'unique_name',
        'pod_id',
        'created_at',
        'updated_at',
        'project',
        'user',
        'last_status',
        'description',
        'config',
        'in_cluster',
        'tags',
        'started_at',
        'finished_at',
        'resources',
        'node_scheduled',
        'num_jobs',
        'num_experiments',
        'dockerfile',
        'backend',
        'commit',
        'bookmarked'
    }

    def setUp(self):
        super().setUp()
        self.obj1 = self.factory_class()
        self.obj1_query = queries.builds_details.get(id=self.obj1.id)
        self.obj2 = self.factory_class()

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1_query).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('user') == self.obj1.user.username
        assert data.pop('project') == self.obj1.project.unique_name
        assert data.pop('last_status') == self.obj1.last_status
        assert data.pop('num_jobs') == Job.objects.filter(build_job=self.obj1).count()
        assert data.pop('num_experiments') == Experiment.objects.filter(build_job=self.obj1).count()
        assert data.pop('commit') == (self.obj1.code_reference.commit
                                      if self.obj1.code_reference else None)
        assert data.pop('bookmarked') is False
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('started_at', None)
        data.pop('finished_at', None)

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_one_with_status(self):
        obj1 = self.factory_class()
        obj1_query = queries.builds_details.get(id=obj1.id)
        data = self.serializer_class(obj1_query).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is None
        assert data['finished_at'] is None

        BuildJobStatus.objects.create(job=obj1, status=JobLifeCycle.SCHEDULED)
        obj1_query.refresh_from_db()
        data = self.serializer_class(obj1_query).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is None

        BuildJobStatus.objects.create(job=obj1, status=JobLifeCycle.SUCCEEDED)
        obj1_query.refresh_from_db()
        data = self.serializer_class(obj1_query).data

        assert set(data.keys()) == self.expected_keys
        assert data['started_at'] is not None
        assert data['finished_at'] is not None

    def test_serialize_many(self):
        data = self.serializer_class(queries.builds_details.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys


@pytest.mark.build_jobs_mark
class TestBuildJobStatusSerializer(BaseTest):
    serializer_class = BuildJobStatusSerializer
    model_class = BuildJobStatus
    factory_class = BuildJobStatusFactory
    expected_keys = {'id', 'uuid', 'job', 'created_at', 'status', 'traceback', 'message', 'details'}

    def setUp(self):
        super().setUp()
        with patch.object(BuildJob, 'set_status') as _:  # noqa
            self.obj1 = self.factory_class()
            self.obj2 = self.factory_class()

    def test_serialize_one(self):
        data = self.serializer_class(self.obj1).data

        assert set(data.keys()) == self.expected_keys
        assert data.pop('uuid') == self.obj1.uuid.hex
        assert data.pop('job') == self.obj1.job.id
        data.pop('created_at')

        for k, v in data.items():
            assert getattr(self.obj1, k) == v

    def test_serialize_many(self):
        data = self.serializer_class(self.model_class.objects.all(), many=True).data
        assert len(data) == 2
        for d in data:
            assert set(d.keys()) == self.expected_keys
