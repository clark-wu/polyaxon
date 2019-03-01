import pytest

from rest_framework import status

from api.bookmarks.serializers import (
    BuildJobBookmarkSerializer,
    ExperimentBookmarkSerializer,
    ExperimentGroupBookmarkSerializer,
    JobBookmarkSerializer,
    ProjectBookmarkSerializer
)
from constants.urls import API_V1
from db.models.bookmarks import Bookmark
from db.models.build_jobs import BuildJob
from db.models.experiment_groups import ExperimentGroup
from db.models.experiments import Experiment
from db.models.jobs import Job
from db.models.projects import Project
from factories.factory_build_jobs import BuildJobFactory
from factories.factory_experiment_groups import ExperimentGroupFactory
from factories.factory_experiments import ExperimentFactory
from factories.factory_jobs import JobFactory
from factories.factory_projects import ProjectFactory
from tests.utils import BaseViewTest


@pytest.mark.bookmarks_mark
class BaseTestBookmarkCreateView(BaseViewTest):
    HAS_AUTH = True
    model_class = None
    factory_class = None
    entity = ''

    def get_url(self):
        return '/{}/{}/{}/{}/{}/bookmark'.format(API_V1,
                                                 self.project.user.username,
                                                 self.project.name,
                                                 self.entity,
                                                 self.object.id)

    def set_object(self):
        self.project = ProjectFactory(user=self.auth_client.user)
        self.object = self.factory_class(project=self.project)  # pylint:disable=not-callable

    def setUp(self):
        super().setUp()
        self.set_object()
        self.url = self.get_url()

    def test_create(self):
        resp = self.auth_client.post(self.url)
        assert resp.status_code == status.HTTP_201_CREATED
        assert Bookmark.objects.count() == 1
        bookmark = Bookmark.objects.first()
        assert bookmark.content_object == self.object
        assert bookmark.user == self.auth_client.user


@pytest.mark.bookmarks_mark
class BaseTestBookmarkDeleteView(BaseViewTest):
    HAS_AUTH = True
    model_class = None
    factory_class = None
    entity = ''

    def get_url(self):
        return '/{}/{}/{}/{}/{}/unbookmark'.format(API_V1,
                                                   self.project.user.username,
                                                   self.project.name,
                                                   self.entity,
                                                   self.object.id)

    def set_object(self):
        self.project = ProjectFactory(user=self.auth_client.user)
        self.object = self.factory_class(project=self.project)  # pylint:disable=not-callable

    def setUp(self):
        super().setUp()
        self.set_object()
        self.url = self.get_url()

    def test_delete(self):
        resp = self.auth_client.delete(self.url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        Bookmark.objects.create(user=self.project.user, content_object=self.object)
        resp = self.auth_client.delete(self.url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert Bookmark.objects.count() == 1
        bookmark = Bookmark.objects.first()
        assert bookmark.content_object == self.object
        assert bookmark.user == self.auth_client.user
        assert bookmark.enabled is False


@pytest.mark.bookmarks_mark
class TestProjectBookmarkCreateView(BaseTestBookmarkCreateView):
    model_class = Project
    factory_class = ProjectFactory
    entity = 'projects'

    def get_url(self):
        return '/{}/{}/{}/bookmark'.format(API_V1,
                                           self.object.user.username,
                                           self.object.name)

    def set_object(self):
        self.project = ProjectFactory(user=self.auth_client.user)
        self.object = self.project


@pytest.mark.bookmarks_mark
class TestProjectBookmarkDeleteView(BaseTestBookmarkDeleteView):
    model_class = Project
    factory_class = ProjectFactory
    entity = 'projects'

    def get_url(self):
        return '/{}/{}/{}/unbookmark'.format(API_V1,
                                             self.object.user.username,
                                             self.object.name)

    def set_object(self):
        self.project = ProjectFactory(user=self.auth_client.user)
        self.object = self.project


@pytest.mark.bookmarks_mark
class TestExperimentBookmarkCreateView(BaseTestBookmarkCreateView):
    model_class = Experiment
    factory_class = ExperimentFactory
    entity = 'experiments'


@pytest.mark.bookmarks_mark
class TestExperimentBookmarkDeleteView(BaseTestBookmarkDeleteView):
    model_class = Experiment
    factory_class = ExperimentFactory
    entity = 'experiments'


@pytest.mark.bookmarks_mark
class TestExperimentGroupBookmarkCreateView(BaseTestBookmarkCreateView):
    model_class = ExperimentGroup
    factory_class = ExperimentGroupFactory
    entity = 'groups'


@pytest.mark.bookmarks_mark
class TestExperimentGroupBookmarkDeleteView(BaseTestBookmarkDeleteView):
    model_class = ExperimentGroup
    factory_class = ExperimentGroupFactory
    entity = 'groups'


@pytest.mark.bookmarks_mark
class TestJobBookmarkCreateView(BaseTestBookmarkCreateView):
    model_class = Job
    factory_class = JobFactory
    entity = 'jobs'


@pytest.mark.bookmarks_mark
class TestJobBookmarkDeleteView(BaseTestBookmarkDeleteView):
    model_class = Job
    factory_class = JobFactory
    entity = 'jobs'


@pytest.mark.bookmarks_mark
class TestBuildBookmarkCreateView(BaseTestBookmarkCreateView):
    model_class = BuildJob
    factory_class = BuildJobFactory
    entity = 'builds'


@pytest.mark.bookmarks_mark
class TestBuildBookmarkDeleteView(BaseTestBookmarkDeleteView):
    model_class = BuildJob
    factory_class = BuildJobFactory
    entity = 'builds'


@pytest.mark.bookmarks_mark
class BaseTestBookmarkListViewV1(BaseViewTest):
    HAS_AUTH = True
    model_class = Bookmark
    serializer_class = None
    factory_class = None
    entity = ''
    num_objects = 3

    def setUp(self):
        super().setUp()
        self.user = self.auth_client.user
        self.url = '/{}/bookmarks/{}/{}'.format(API_V1, self.user.username, self.entity)
        self.objects = []
        for _ in range(self.num_objects):
            obj = self.factory_class(user=self.user)  # pylint:disable=not-callable
            self.objects.append(Bookmark.objects.create(user=self.user, content_object=obj))

        # Other user objects
        obj = self.factory_class()  # pylint:disable=not-callable
        self.other_object = Bookmark.objects.create(
            user=obj.user,
            content_object=self.factory_class())  # pylint:disable=not-callable
        self.url_other = '/{}/bookmarks/{}/{}'.format(API_V1, obj.user.username, self.entity)

        self.queryset = self.model_class.objects.filter(user=self.user)
        self.queryset = self.queryset.order_by('-updated_at')

    def test_get(self):
        resp = self.auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None
        assert resp.data['count'] == len(self.objects)

        data = resp.data['results']
        assert len(data) == self.queryset.count()
        assert data == self.serializer_class(self.queryset, many=True).data  # noqa

    def test_get_others(self):
        resp = self.auth_client.get(self.url_other)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None
        assert resp.data['count'] == 0

    def test_pagination(self):
        limit = self.num_objects - 1
        resp = self.auth_client.get("{}?limit={}".format(self.url, limit))
        assert resp.status_code == status.HTTP_200_OK

        next_page = resp.data.get('next')
        assert next_page is not None
        assert resp.data['count'] == self.queryset.count()

        data = resp.data['results']
        assert len(data) == limit
        assert data == self.serializer_class(self.queryset[:limit], many=True).data  # noqa

        resp = self.auth_client.get(next_page)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None

        data = resp.data['results']
        assert len(data) == 1
        assert data == self.serializer_class(self.queryset[limit:], many=True).data  # noqa


@pytest.mark.bookmarks_mark
class TestBuildBookmarkListView(BaseTestBookmarkListViewV1):
    HAS_AUTH = True
    serializer_class = BuildJobBookmarkSerializer
    factory_class = BuildJobFactory
    entity = 'builds'


@pytest.mark.bookmarks_mark
class TestJobBookmarkListView(BaseTestBookmarkListViewV1):
    HAS_AUTH = True
    serializer_class = JobBookmarkSerializer
    factory_class = JobFactory
    entity = 'jobs'


@pytest.mark.bookmarks_mark
class TestExperimentBookmarkListView(BaseTestBookmarkListViewV1):
    HAS_AUTH = True
    serializer_class = ExperimentBookmarkSerializer
    factory_class = ExperimentFactory
    entity = 'experiments'


@pytest.mark.bookmarks_mark
class TestExperimentGroupBookmarkListView(BaseTestBookmarkListViewV1):
    HAS_AUTH = True
    serializer_class = ExperimentGroupBookmarkSerializer
    factory_class = ExperimentGroupFactory
    entity = 'groups'


@pytest.mark.bookmarks_mark
class TestProjectBookmarkListView(BaseTestBookmarkListViewV1):
    HAS_AUTH = True
    serializer_class = ProjectBookmarkSerializer
    factory_class = ProjectFactory
    entity = 'projects'


del BaseTestBookmarkCreateView
del BaseTestBookmarkDeleteView
del BaseTestBookmarkListViewV1
