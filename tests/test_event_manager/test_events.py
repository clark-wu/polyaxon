from uuid import uuid1

import pytest

from django.contrib.contenttypes.models import ContentType

from constants import user_system
from event_manager.event import Attribute, Event
from event_manager.events import (
    archive,
    bookmark,
    build_job,
    chart_view,
    cluster,
    experiment,
    experiment_group,
    experiment_job,
    job,
    notebook,
    permission,
    project,
    repo,
    search,
    superuser,
    tensorboard,
    user
)
from event_manager.events.experiment import ExperimentSucceededEvent
from factories.factory_experiments import ExperimentFactory
from libs.json_utils import loads
from tests.utils import BaseTest


@pytest.mark.events_mark
class TestEvents(BaseTest):
    def test_events_subjects(self):  # pylint:disable=too-many-statements
        # Cluster
        assert cluster.ClusterCreatedEvent.get_event_subject() == 'cluster'
        assert cluster.ClusterUpdatedEvent.get_event_subject() == 'cluster'
        assert cluster.ClusterNodeCreatedEvent.get_event_subject() == 'cluster_node'
        assert cluster.ClusterNodeUpdatedEvent.get_event_subject() == 'cluster_node'
        assert cluster.ClusterNodeDeletedEvent.get_event_subject() == 'cluster_node'
        assert cluster.ClusterNodeGPU.get_event_subject() == 'cluster_node'

        # Experiment
        assert experiment.ExperimentCreatedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentUpdatedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentDeletedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentArchivedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentRestoredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentBookmarkedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentUnBookmarkedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentStoppedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentResumedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentRestartedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentCopiedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentNewStatusEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentNewMetricEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentSucceededEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentFailedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentDoneEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentResourcesViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentLogsViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentOutputsDownloadedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentStatusesViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentJobsViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentMetricsViewedEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentDeletedTriggeredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentStoppedTriggeredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentResumedTriggeredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentCleanedTriggeredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentRestartedTriggeredEvent.get_event_subject() == 'experiment'
        assert experiment.ExperimentCopiedTriggeredEvent.get_event_subject() == 'experiment'

        # Experiment group
        assert (experiment_group.ExperimentGroupCreatedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupUpdatedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupDeletedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupViewedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupArchivedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupRestoredEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupBookmarkedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupUnBookmarkedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupStoppedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupResumedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupDoneEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupNewStatusEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupExperimentsViewedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupStatusesViewedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupMetricsViewedEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupIterationEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupRandomEvent.get_event_subject() ==
                'experiment_group')
        assert experiment_group.ExperimentGroupGridEvent.get_event_subject() == 'experiment_group'
        assert (experiment_group.ExperimentGroupHyperbandEvent.get_event_subject() ==
                'experiment_group')
        assert experiment_group.ExperimentGroupBOEvent.get_event_subject() == 'experiment_group'
        assert (experiment_group.ExperimentGroupDeletedTriggeredEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupStoppedTriggeredEvent.get_event_subject() ==
                'experiment_group')
        assert (experiment_group.ExperimentGroupResumedTriggeredEvent.get_event_subject() ==
                'experiment_group')

        # Experiment job
        assert experiment_job.ExperimentJobViewedEvent.get_event_subject() == 'experiment_job'
        assert (experiment_job.ExperimentJobResourcesViewedEvent.get_event_subject() ==
                'experiment_job')
        assert experiment_job.ExperimentJobLogsViewedEvent.get_event_subject() == 'experiment_job'
        assert (experiment_job.ExperimentJobStatusesViewedEvent.get_event_subject() ==
                'experiment_job')
        assert (experiment_job.ExperimentJobNewStatusEvent.get_event_subject() ==
                'experiment_job')

        # Notebook
        assert notebook.NotebookStartedEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookStartedTriggeredEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookSoppedEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookSoppedTriggeredEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookCleanedTriggeredEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookViewedEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookNewStatusEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookFailedEvent.get_event_subject() == 'notebook'
        assert notebook.NotebookSucceededEvent.get_event_subject() == 'notebook'

        # Job
        assert job.JobCreatedEvent.get_event_subject() == 'job'
        assert job.JobUpdatedEvent.get_event_subject() == 'job'
        assert job.JobStartedEvent.get_event_subject() == 'job'
        assert job.JobStartedTriggeredEvent.get_event_subject() == 'job'
        assert job.JobSoppedEvent.get_event_subject() == 'job'
        assert job.JobSoppedTriggeredEvent.get_event_subject() == 'job'
        assert job.JobCleanedTriggeredEvent.get_event_subject() == 'job'
        assert job.JobViewedEvent.get_event_subject() == 'job'
        assert job.JobArchivedEvent.get_event_subject() == 'job'
        assert job.JobRestoredEvent.get_event_subject() == 'job'
        assert job.JobBookmarkedEvent.get_event_subject() == 'job'
        assert job.JobUnBookmarkedEvent.get_event_subject() == 'job'
        assert job.JobNewStatusEvent.get_event_subject() == 'job'
        assert job.JobFailedEvent.get_event_subject() == 'job'
        assert job.JobSucceededEvent.get_event_subject() == 'job'
        assert job.JobDoneEvent.get_event_subject() == 'job'
        assert job.JobDeletedEvent.get_event_subject() == 'job'
        assert job.JobDeletedTriggeredEvent.get_event_subject() == 'job'
        assert job.JobLogsViewedEvent.get_event_subject() == 'job'
        assert job.JobRestartedEvent.get_event_subject() == 'job'
        assert job.JobRestartedTriggeredEvent.get_event_subject() == 'job'
        assert job.JobStatusesViewedEvent.get_event_subject() == 'job'
        assert job.JobOutputsDownloadedEvent.get_event_subject() == 'job'

        # BuildJob
        assert build_job.BuildJobCreatedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobUpdatedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobStartedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobStartedTriggeredEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobSoppedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobSoppedTriggeredEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobCleanedTriggeredEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobViewedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobArchivedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobRestoredEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobBookmarkedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobUnBookmarkedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobNewStatusEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobFailedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobSucceededEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobDoneEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobDeletedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobDeletedTriggeredEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobLogsViewedEvent.get_event_subject() == 'build_job'
        assert build_job.BuildJobStatusesViewedEvent.get_event_subject() == 'build_job'

        # Bookmarks
        assert bookmark.BookmarkBuildJobsViewedEvent.get_event_subject() == 'bookmark'
        assert bookmark.BookmarkJobsViewedEvent.get_event_subject() == 'bookmark'
        assert bookmark.BookmarkExperimentsViewedEvent.get_event_subject() == 'bookmark'
        assert bookmark.BookmarkExperimentGroupsViewedEvent.get_event_subject() == 'bookmark'
        assert bookmark.BookmarkProjectsViewedEvent.get_event_subject() == 'bookmark'

        # Archives
        assert archive.ArchiveBuildJobsViewedEvent.get_event_subject() == 'archive'
        assert archive.ArchiveJobsViewedEvent.get_event_subject() == 'archive'
        assert archive.ArchiveExperimentsViewedEvent.get_event_subject() == 'archive'
        assert archive.ArchiveExperimentGroupsViewedEvent.get_event_subject() == 'archive'
        assert archive.ArchiveProjectsViewedEvent.get_event_subject() == 'archive'

        # Searches
        assert search.SearchCreatedEvent.get_event_subject() == 'search'
        assert search.SearchDeletedEvent.get_event_subject() == 'search'

        # Chart view
        assert chart_view.ChartViewCreatedEvent.get_event_subject() == 'chart_view'
        assert chart_view.ChartViewDeletedEvent.get_event_subject() == 'chart_view'

        # Permission
        assert permission.PermissionProjectDeniedEvent.get_event_subject() == 'project'
        assert permission.PermissionRepoDeniedEvent.get_event_subject() == 'repo'
        assert (permission.PermissionExperimentGroupDeniedEvent.get_event_subject() ==
                'experiment_group')
        assert permission.PermissionExperimentDeniedEvent.get_event_subject() == 'experiment'
        assert permission.PermissionTensorboardDeniedEvent.get_event_subject() == 'tensorboard'
        assert permission.PermissionNotebookDeniedEvent.get_event_subject() == 'notebook'
        assert permission.PermissionBuildJobDeniedEvent.get_event_subject() == 'build_job'
        assert permission.PermissionExperimentJobDeniedEvent.get_event_subject() == 'experiment_job'
        assert permission.PermissionClusterDeniedEvent.get_event_subject() == 'cluster'
        assert permission.PermissionUserRoleEvent.get_event_subject() == 'superuser'

        # Project
        assert project.ProjectCreatedEvent.get_event_subject() == 'project'
        assert project.ProjectUpdatedEvent.get_event_subject() == 'project'
        assert project.ProjectDeletedEvent.get_event_subject() == 'project'
        assert project.ProjectDeletedTriggeredEvent.get_event_subject() == 'project'
        assert project.ProjectViewedEvent.get_event_subject() == 'project'
        assert project.ProjectArchivedEvent.get_event_subject() == 'project'
        assert project.ProjectRestoredEvent.get_event_subject() == 'project'
        assert project.ProjectBookmarkedEvent.get_event_subject() == 'project'
        assert project.ProjectUnBookmarkedEvent.get_event_subject() == 'project'
        assert project.ProjectSetPublicEvent.get_event_subject() == 'project'
        assert project.ProjectSetPrivateEvent.get_event_subject() == 'project'
        assert project.ProjectExperimentsViewedEvent.get_event_subject() == 'project'
        assert project.ProjectExperimentGroupsViewedEvent.get_event_subject() == 'project'
        assert project.ProjectJobsViewedEvent.get_event_subject() == 'project'
        assert project.ProjectBuildsViewedEvent.get_event_subject() == 'project'
        assert project.ProjectTensorboardsViewedEvent.get_event_subject() == 'project'

        # Repo
        assert repo.RepoCreatedEvent.get_event_subject() == 'repo'
        assert repo.RepoNewCommitEvent.get_event_subject() == 'repo'

        # Superuser
        assert superuser.SuperUserRoleGrantedEvent.get_event_subject() == 'superuser'
        assert superuser.SuperUserRoleRevokedEvent.get_event_subject() == 'superuser'

        # Tensorboard
        assert tensorboard.TensorboardStartedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardStartedTriggeredEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardSoppedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardSoppedTriggeredEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardCleanedTriggeredEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardViewedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardBookmarkedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardUnBookmarkedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardNewStatusEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardFailedEvent.get_event_subject() == 'tensorboard'
        assert tensorboard.TensorboardSucceededEvent.get_event_subject() == 'tensorboard'

        # User
        assert user.UserRegisteredEvent.get_event_subject() == 'user'
        assert user.UserUpdatedEvent.get_event_subject() == 'user'
        assert user.UserActivatedEvent.get_event_subject() == 'user'
        assert user.UserDeletedEvent.get_event_subject() == 'user'
        assert user.UserLDAPEvent.get_event_subject() == 'user'
        assert user.UserGITHUBEvent.get_event_subject() == 'user'
        assert user.UserGITLABEvent.get_event_subject() == 'user'
        assert user.UserBITBUCKETEvent.get_event_subject() == 'user'
        assert user.UserAZUREEvent.get_event_subject() == 'user'

    def test_events_actions(self):  # pylint:disable=too-many-statements
        # Cluster
        assert cluster.ClusterCreatedEvent.get_event_action() is None
        assert cluster.ClusterUpdatedEvent.get_event_action() is None
        assert cluster.ClusterNodeCreatedEvent.get_event_action() is None
        assert cluster.ClusterNodeUpdatedEvent.get_event_action() is None
        assert cluster.ClusterNodeDeletedEvent.get_event_action() is None
        assert cluster.ClusterNodeGPU.get_event_action() is None

        # Experiment
        assert experiment.ExperimentCreatedEvent.get_event_action() == 'created'
        assert experiment.ExperimentUpdatedEvent.get_event_action() == 'updated'
        assert experiment.ExperimentDeletedEvent.get_event_action() is None
        assert experiment.ExperimentViewedEvent.get_event_action() == 'viewed'
        assert experiment.ExperimentArchivedEvent.get_event_action() == 'archived'
        assert experiment.ExperimentRestoredEvent.get_event_action() == 'restored'
        assert experiment.ExperimentBookmarkedEvent.get_event_action() == 'bookmarked'
        assert experiment.ExperimentUnBookmarkedEvent.get_event_action() == 'unbookmarked'
        assert experiment.ExperimentStoppedEvent.get_event_action() is None
        assert experiment.ExperimentResumedEvent.get_event_action() is None
        assert experiment.ExperimentRestartedEvent.get_event_action() is None
        assert experiment.ExperimentCopiedEvent.get_event_action() is None
        assert experiment.ExperimentNewStatusEvent.get_event_action() is None
        assert experiment.ExperimentNewMetricEvent.get_event_action() is None
        assert experiment.ExperimentSucceededEvent.get_event_action() is None
        assert experiment.ExperimentFailedEvent.get_event_action() is None
        assert experiment.ExperimentDoneEvent.get_event_action() is None
        assert experiment.ExperimentResourcesViewedEvent.get_event_action() == 'resources_viewed'
        assert experiment.ExperimentLogsViewedEvent.get_event_action() == 'logs_viewed'
        assert (experiment.ExperimentOutputsDownloadedEvent.get_event_action() ==
                'outputs_downloaded')
        assert experiment.ExperimentStatusesViewedEvent.get_event_action() == 'statuses_viewed'
        assert experiment.ExperimentJobsViewedEvent.get_event_action() == 'jobs_viewed'
        assert experiment.ExperimentMetricsViewedEvent.get_event_action() == 'metrics_viewed'
        assert experiment.ExperimentCleanedTriggeredEvent.get_event_action() is None
        assert experiment.ExperimentDeletedTriggeredEvent.get_event_action() == 'deleted'
        assert experiment.ExperimentStoppedTriggeredEvent.get_event_action() == 'stopped'
        assert experiment.ExperimentResumedTriggeredEvent.get_event_action() == 'resumed'
        assert experiment.ExperimentRestartedTriggeredEvent.get_event_action() == 'restarted'
        assert experiment.ExperimentCopiedTriggeredEvent.get_event_action() == 'copied'

        # Experiment group
        assert experiment_group.ExperimentGroupCreatedEvent.get_event_action() == 'created'
        assert experiment_group.ExperimentGroupUpdatedEvent.get_event_action() == 'updated'
        assert experiment_group.ExperimentGroupDeletedEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupViewedEvent.get_event_action() == 'viewed'
        assert experiment_group.ExperimentGroupArchivedEvent.get_event_action() == 'archived'
        assert experiment_group.ExperimentGroupRestoredEvent.get_event_action() == 'restored'
        assert experiment_group.ExperimentGroupBookmarkedEvent.get_event_action() == 'bookmarked'
        assert (experiment_group.ExperimentGroupUnBookmarkedEvent.get_event_action() ==
                'unbookmarked')
        assert experiment_group.ExperimentGroupStoppedEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupResumedEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupDoneEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupNewStatusEvent.get_event_action() is None
        assert (experiment_group.ExperimentGroupExperimentsViewedEvent.get_event_action() ==
                'experiments_viewed')
        assert (experiment_group.ExperimentGroupStatusesViewedEvent.get_event_action() ==
                'statuses_viewed')
        assert (experiment_group.ExperimentGroupMetricsViewedEvent.get_event_action() ==
                'metrics_viewed')
        assert experiment_group.ExperimentGroupIterationEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupRandomEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupGridEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupHyperbandEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupBOEvent.get_event_action() is None
        assert experiment_group.ExperimentGroupDeletedTriggeredEvent.get_event_action() == 'deleted'
        assert experiment_group.ExperimentGroupStoppedTriggeredEvent.get_event_action() == 'stopped'
        assert experiment_group.ExperimentGroupResumedTriggeredEvent.get_event_action() == 'resumed'

        # Experiment job
        assert experiment_job.ExperimentJobViewedEvent.get_event_action() == 'viewed'
        assert (experiment_job.ExperimentJobResourcesViewedEvent.get_event_action() ==
                'resources_viewed')
        assert experiment_job.ExperimentJobLogsViewedEvent.get_event_action() == 'logs_viewed'
        assert (experiment_job.ExperimentJobStatusesViewedEvent.get_event_action() ==
                'statuses_viewed')
        assert experiment_job.ExperimentJobNewStatusEvent.get_event_action() is None

        # Notebook
        assert notebook.NotebookStartedEvent.get_event_action() is None
        assert notebook.NotebookStartedTriggeredEvent.get_event_action() == 'started'
        assert notebook.NotebookSoppedEvent.get_event_action() is None
        assert notebook.NotebookSoppedTriggeredEvent.get_event_action() == 'stopped'
        assert notebook.NotebookCleanedTriggeredEvent.get_event_action() is None
        assert notebook.NotebookViewedEvent.get_event_action() == 'viewed'
        assert notebook.NotebookNewStatusEvent.get_event_action() is None
        assert notebook.NotebookFailedEvent.get_event_action() is None
        assert notebook.NotebookSucceededEvent.get_event_action() is None

        # Job
        assert job.JobCreatedEvent.get_event_action() == 'created'
        assert job.JobUpdatedEvent.get_event_action() == 'updated'
        assert job.JobStartedEvent.get_event_action() is None
        assert job.JobStartedTriggeredEvent.get_event_action() == 'started'
        assert job.JobSoppedEvent.get_event_action() is None
        assert job.JobSoppedTriggeredEvent.get_event_action() == 'stopped'
        assert job.JobCleanedTriggeredEvent.get_event_action() is None
        assert job.JobViewedEvent.get_event_action() == 'viewed'
        assert job.JobBookmarkedEvent.get_event_action() == 'bookmarked'
        assert job.JobUnBookmarkedEvent.get_event_action() == 'unbookmarked'
        assert job.JobNewStatusEvent.get_event_action() is None
        assert job.JobFailedEvent.get_event_action() is None
        assert job.JobSucceededEvent.get_event_action() is None
        assert job.JobDoneEvent.get_event_action() is None
        assert job.JobDeletedEvent.get_event_action() is None
        assert job.JobDeletedTriggeredEvent.get_event_action() == 'deleted'
        assert job.JobLogsViewedEvent.get_event_action() == 'logs_viewed'
        assert job.JobRestartedEvent.get_event_action() is None
        assert job.JobRestartedTriggeredEvent.get_event_action() == 'restarted'
        assert job.JobStatusesViewedEvent.get_event_action() == 'statuses_viewed'
        assert job.JobOutputsDownloadedEvent.get_event_action() == 'outputs_downloaded'

        # Build job
        assert build_job.BuildJobCreatedEvent.get_event_action() == 'created'
        assert build_job.BuildJobUpdatedEvent.get_event_action() == 'updated'
        assert build_job.BuildJobStartedEvent.get_event_action() is None
        assert build_job.BuildJobStartedTriggeredEvent.get_event_action() == 'started'
        assert build_job.BuildJobSoppedEvent.get_event_action() is None
        assert build_job.BuildJobSoppedTriggeredEvent.get_event_action() == 'stopped'
        assert build_job.BuildJobCleanedTriggeredEvent.get_event_action() is None
        assert build_job.BuildJobViewedEvent.get_event_action() == 'viewed'
        assert build_job.BuildJobArchivedEvent.get_event_action() == 'archived'
        assert build_job.BuildJobRestoredEvent.get_event_action() == 'restored'
        assert build_job.BuildJobBookmarkedEvent.get_event_action() == 'bookmarked'
        assert build_job.BuildJobUnBookmarkedEvent.get_event_action() == 'unbookmarked'
        assert build_job.BuildJobNewStatusEvent.get_event_action() is None
        assert build_job.BuildJobFailedEvent.get_event_action() is None
        assert build_job.BuildJobSucceededEvent.get_event_action() is None
        assert build_job.BuildJobDoneEvent.get_event_action() is None
        assert build_job.BuildJobDeletedEvent.get_event_action() is None
        assert build_job.BuildJobDeletedTriggeredEvent.get_event_action() == 'deleted'
        assert build_job.BuildJobLogsViewedEvent.get_event_action() == 'logs_viewed'
        assert build_job.BuildJobStatusesViewedEvent.get_event_action() == 'statuses_viewed'

        # Bookmarks
        assert bookmark.BookmarkBuildJobsViewedEvent.get_event_action() == 'builds_viewed'
        assert bookmark.BookmarkJobsViewedEvent.get_event_action() == 'jobs_viewed'
        assert bookmark.BookmarkExperimentsViewedEvent.get_event_action() == 'experiments_viewed'
        assert (bookmark.BookmarkExperimentGroupsViewedEvent.get_event_action() ==
                'experiment_groups_viewed')
        assert bookmark.BookmarkProjectsViewedEvent.get_event_action() == 'projects_viewed'

        # Archive
        assert archive.ArchiveBuildJobsViewedEvent.get_event_action() == 'builds_viewed'
        assert archive.ArchiveJobsViewedEvent.get_event_action() == 'jobs_viewed'
        assert archive.ArchiveExperimentsViewedEvent.get_event_action() == 'experiments_viewed'
        assert (archive.ArchiveExperimentGroupsViewedEvent.get_event_action() ==
                'experiment_groups_viewed')
        assert archive.ArchiveProjectsViewedEvent.get_event_action() == 'projects_viewed'

        # Searches
        assert search.SearchCreatedEvent.get_event_action() == 'created'
        assert search.SearchDeletedEvent.get_event_action() == 'deleted'

        # Chart views
        assert chart_view.ChartViewCreatedEvent.get_event_action() == 'created'
        assert chart_view.ChartViewDeletedEvent.get_event_action() == 'deleted'

        # Permission
        assert permission.PermissionProjectDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionRepoDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionExperimentGroupDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionExperimentDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionTensorboardDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionNotebookDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionBuildJobDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionExperimentJobDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionClusterDeniedEvent.get_event_action() == 'denied'
        assert permission.PermissionUserRoleEvent.get_event_action() == 'denied'

        # Project
        assert project.ProjectCreatedEvent.get_event_action() == 'created'
        assert project.ProjectUpdatedEvent.get_event_action() == 'updated'
        assert project.ProjectDeletedEvent.get_event_action() is None
        assert project.ProjectDeletedTriggeredEvent.get_event_action() == 'deleted'
        assert project.ProjectViewedEvent.get_event_action() == 'viewed'
        assert project.ProjectArchivedEvent.get_event_action() == 'archived'
        assert project.ProjectRestoredEvent.get_event_action() == 'restored'
        assert project.ProjectBookmarkedEvent.get_event_action() == 'bookmarked'
        assert project.ProjectUnBookmarkedEvent.get_event_action() == 'unbookmarked'
        assert project.ProjectSetPublicEvent.get_event_action() is None
        assert project.ProjectSetPrivateEvent.get_event_action() is None
        assert project.ProjectExperimentsViewedEvent.get_event_action() == 'experiments_viewed'
        assert (project.ProjectExperimentGroupsViewedEvent.get_event_action() ==
                'experiment_groups_viewed')
        assert project.ProjectJobsViewedEvent.get_event_action() == 'jobs_viewed'
        assert project.ProjectBuildsViewedEvent.get_event_action() == 'builds_viewed'
        assert project.ProjectTensorboardsViewedEvent.get_event_action() == 'tensorboards_viewed'

        # Repo
        assert repo.RepoCreatedEvent.get_event_action() == 'created'
        assert repo.RepoNewCommitEvent.get_event_action() == 'new_commit'

        # Superuser
        assert superuser.SuperUserRoleGrantedEvent.get_event_action() == 'granted'
        assert superuser.SuperUserRoleRevokedEvent.get_event_action() == 'revoked'

        # Tensorboard
        assert tensorboard.TensorboardStartedEvent.get_event_action() is None
        assert tensorboard.TensorboardStartedTriggeredEvent.get_event_action() == 'started'
        assert tensorboard.TensorboardSoppedEvent.get_event_action() is None
        assert tensorboard.TensorboardSoppedTriggeredEvent.get_event_action() == 'stopped'
        assert tensorboard.TensorboardCleanedTriggeredEvent.get_event_action() is None
        assert tensorboard.TensorboardViewedEvent.get_event_action() == 'viewed'
        assert tensorboard.TensorboardBookmarkedEvent.get_event_action() == 'bookmarked'
        assert tensorboard.TensorboardUnBookmarkedEvent.get_event_action() == 'unbookmarked'
        assert tensorboard.TensorboardNewStatusEvent.get_event_action() is None
        assert tensorboard.TensorboardFailedEvent.get_event_action() is None
        assert tensorboard.TensorboardSucceededEvent.get_event_action() is None

        # User
        assert user.UserRegisteredEvent.get_event_action() == 'registered'
        assert user.UserUpdatedEvent.get_event_action() == 'updated'
        assert user.UserActivatedEvent.get_event_action() == 'activated'
        assert user.UserDeletedEvent.get_event_action() == 'deleted'
        assert user.UserLDAPEvent.get_event_action() is None
        assert user.UserGITHUBEvent.get_event_action() == 'auth'
        assert user.UserGITLABEvent.get_event_action() == 'auth'
        assert user.UserBITBUCKETEvent.get_event_action() == 'auth'
        assert user.UserAZUREEvent.get_event_action() == 'auth'

    def test_serialize(self):
        class DummyEvent(Event):
            event_type = 'dummy.event'
            attributes = (
                Attribute('attr1'),
            )

        event = DummyEvent(attr1='test')
        event_serialized = event.serialize(dumps=False)
        assert event_serialized['type'] == 'dummy.event'
        assert event_serialized['uuid'] is not None
        assert event_serialized['timestamp'] is not None
        assert event_serialized['data']['attr1'] == 'test'

        event_serialized_dump = event.serialize(dumps=True)
        assert event_serialized == loads(event_serialized_dump)

    def test_serialize_with_instance(self):
        instance = ExperimentFactory()
        event = ExperimentSucceededEvent.from_instance(instance=instance,
                                                       actor_id=1,
                                                       actor_name='user')
        event_serialized = event.serialize(dumps=False, include_instance_info=True)
        instance_contenttype = ContentType.objects.get_for_model(instance).id
        assert event_serialized['instance_id'] == instance.id
        assert event_serialized['instance_contenttype'] == instance_contenttype

    def test_from_event_data(self):
        instance = ExperimentFactory()
        event = ExperimentSucceededEvent.from_instance(instance=instance,
                                                       actor_id=1,
                                                       actor_name='user')
        assert event.ref_id is None
        event_serialized = event.serialize(dumps=False, include_instance_info=True)
        assert event_serialized.get('ref_id') is None
        new_event = ExperimentSucceededEvent.from_event_data(event_data=event_serialized)
        assert new_event.serialize(include_instance_info=True) == event_serialized

        # Add ref id
        event.ref_id = uuid1()
        event_serialized = event.serialize(dumps=False, include_instance_info=True)
        assert event_serialized['ref_id'] == event.ref_id.hex
        new_event = ExperimentSucceededEvent.from_event_data(event_data=event_serialized)
        assert new_event.ref_id == event.ref_id
        assert new_event.serialize(include_instance_info=True) == event_serialized

    def test_get_value_from_instance(self):
        class DummyEvent(Event):
            event_type = 'dummy.event'

        class SimpleObject(object):
            attr1 = 'test'

        class ComposedObject(object):
            attr2 = SimpleObject()

        value = DummyEvent.get_value_from_instance(attr='attr1',
                                                   instance=SimpleObject())
        assert value == 'test'

        value = DummyEvent.get_value_from_instance(attr='attr2',
                                                   instance=SimpleObject())
        assert value is None

        value = DummyEvent.get_value_from_instance(attr='attr2.attr1',
                                                   instance=ComposedObject())
        assert value == 'test'

        value = DummyEvent.get_value_from_instance(attr='attr2.attr3',
                                                   instance=ComposedObject())
        assert value is None

        value = DummyEvent.get_value_from_instance(attr='attr2.attr1.attr3',
                                                   instance=ComposedObject())
        assert value is None

        value = DummyEvent.get_value_from_instance(attr='attr2.attr4.attr3',
                                                   instance=SimpleObject())
        assert value is None

    def test_from_instance_simple_event(self):
        class DummyEvent(Event):
            event_type = 'dummy.event'
            attributes = (
                Attribute('attr1'),
            )

        class DummyObject(object):
            attr1 = 'test'

        obj = DummyObject()
        event = DummyEvent.from_instance(obj)
        event_serialized = event.serialize(dumps=False)
        assert event_serialized['type'] == 'dummy.event'
        assert event_serialized['uuid'] is not None
        assert event_serialized['timestamp'] is not None
        assert event_serialized['data']['attr1'] == 'test'

    def test_from_instance_nested_event(self):
        class DummyEvent(Event):
            event_type = 'dummy.event'
            attributes = (
                Attribute('attr1'),
                Attribute('attr2.attr3'),
                Attribute('attr2.attr4', is_required=False),
            )

        class DummyObject(object):
            class NestedObject(object):
                attr3 = 'test2'

            attr1 = 'test'
            attr2 = NestedObject()

        obj = DummyObject()
        event = DummyEvent.from_instance(obj)
        event_serialized = event.serialize(dumps=False)
        assert event_serialized['type'] == 'dummy.event'
        assert event_serialized['uuid'] is not None
        assert event_serialized['timestamp'] is not None
        assert event_serialized['data']['attr1'] == 'test'
        assert event_serialized['data']['attr2.attr3'] == 'test2'
        assert event_serialized['data']['attr2.attr4'] is None

    def test_actor(self):
        class DummyEvent1(Event):
            event_type = 'dummy.event'
            actor = True
            attributes = (
                Attribute('attr1'),
            )

        class DummyEvent2(Event):
            event_type = 'dummy.event'
            actor = True
            actor_id = 'some_actor_id'
            actor_name = 'some_actor_name'
            attributes = (
                Attribute('attr1'),
            )

        class DummyObject1(object):
            attr1 = 'test'

        class DummyObject2(object):
            attr1 = 'test'
            some_actor_id = 1
            some_actor_name = 'foo'

        # Not providing actor_id raises
        obj = DummyObject1()
        with self.assertRaises(ValueError):
            DummyEvent1.from_instance(obj)

        # Providing actor_id and not actor_name raises
        with self.assertRaises(ValueError):
            DummyEvent1.from_instance(obj, actor_id=1)

        # Providing system actor id without actor_name does not raise
        event = DummyEvent1.from_instance(obj, actor_id=user_system.USER_SYSTEM_ID)
        assert event.data['actor_id'] == user_system.USER_SYSTEM_ID
        assert event.data['actor_name'] == user_system.USER_SYSTEM_NAME

        # Providing actor_id and actor_name does not raise
        event = DummyEvent1.from_instance(obj, actor_id=1, actor_name='foo')
        assert event.data['actor_id'] == 1
        assert event.data['actor_name'] == 'foo'

        # Using an instance that has the actor properties
        obj2 = DummyObject2()
        event = DummyEvent2.from_instance(obj2)
        assert event.data['some_actor_id'] == 1
        assert event.data['some_actor_name'] == 'foo'

        # Using an instance that has the actor properties and overriding the actor
        event = DummyEvent2.from_instance(obj2,
                                          some_actor_id=user_system.USER_SYSTEM_ID,
                                          some_actor_name=user_system.USER_SYSTEM_NAME)
        assert event.data['some_actor_id'] == user_system.USER_SYSTEM_ID
        assert event.data['some_actor_name'] == user_system.USER_SYSTEM_NAME
