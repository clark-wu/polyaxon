import os

from unittest.mock import patch

import mock
import pytest

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import MULTIPART_CONTENT
from django.utils import timezone

import stores

from constants.experiments import ExperimentLifeCycle
from constants.jobs import JobLifeCycle
from constants.urls import API_V1
from crons.tasks.experiments_statuses import experiments_sync_jobs_statuses
from db.managers.deleted import ArchivedManager, LiveManager
from db.models.build_jobs import BuildJobStatus
from db.models.cloning_strategies import CloningStrategy
from db.models.experiment_jobs import ExperimentJob, ExperimentJobStatus
from db.models.experiments import Experiment, ExperimentStatus
from db.models.job_resources import JobResources
from factories.factory_build_jobs import BuildJobFactory
from factories.factory_experiment_groups import ExperimentGroupFactory
from factories.factory_experiments import (
    ExperimentFactory,
    ExperimentJobFactory,
    ExperimentJobStatusFactory,
    ExperimentStatusFactory
)
from factories.factory_projects import ProjectFactory
from factories.factory_repos import RepoFactory
from factories.fixtures import (
    exec_experiment_ext_repo_spec_content,
    exec_experiment_resources_content,
    exec_experiment_resources_parsed_content,
    exec_experiment_spec_content,
    experiment_spec_content
)
from scheduler.tasks.experiments import copy_experiment, experiments_build, experiments_set_metrics
from schemas.specifications import ExperimentSpecification
from schemas.tasks import TaskType
from tests.fixtures import start_experiment_value
from tests.utils import BaseTest, BaseViewTest


@pytest.mark.experiments_mark
class TestExperimentModel(BaseTest):
    DISABLE_EXECUTOR = False
    DISABLE_RUNNER = False

    def test_create_experiment_with_no_spec_or_declarations(self):
        experiment = ExperimentFactory(declarations=None, config=None)
        assert experiment.declarations is None
        assert experiment.specification is None

    def test_create_experiment_with_no_spec_and_declarations(self):
        experiment = ExperimentFactory(declarations={'lr': 0.1, 'dropout': 0.5}, config=None)
        assert experiment.declarations == {'lr': 0.1, 'dropout': 0.5}
        assert experiment.specification is None

    def test_create_experiment_with_spec_trigger_declarations_creation(self):
        experiment = ExperimentFactory(config=exec_experiment_resources_parsed_content.parsed_data)
        assert experiment.declarations == {'lr': 0.1, 'dropout': 0.5}
        assert isinstance(experiment.specification, ExperimentSpecification)

    def test_experiment_creation_triggers_status_creation_mocks(self):
        with patch.object(Experiment, 'set_status') as mock_fct2:
            ExperimentFactory()
        assert mock_fct2.call_count == 1

    def test_status_update_results_in_new_updated_at_datetime_experiment(self):
        experiment = ExperimentFactory()
        updated_at = experiment.updated_at
        # Create new status
        ExperimentStatus.objects.create(experiment=experiment, status=ExperimentLifeCycle.STARTING)
        experiment.refresh_from_db()
        assert updated_at < experiment.updated_at
        updated_at = experiment.updated_at
        # Create status Using set_status
        experiment.set_status(ExperimentLifeCycle.FAILED)
        experiment.refresh_from_db()
        assert updated_at < experiment.updated_at

    def test_status_update_results_in_new_updated_at_datetime_experiment_job(self):
        experiment_job = ExperimentJobFactory()
        updated_at = experiment_job.updated_at
        # Create new status
        ExperimentJobStatus.objects.create(job=experiment_job, status=ExperimentLifeCycle.BUILDING)
        experiment_job.refresh_from_db()
        assert updated_at < experiment_job.updated_at
        updated_at = experiment_job.updated_at
        # Create status Using set_status
        experiment_job.set_status(ExperimentLifeCycle.FAILED)
        experiment_job.refresh_from_db()
        assert updated_at < experiment_job.updated_at

    def test_restart(self):
        experiment = ExperimentFactory()
        new_experiment = experiment.restart()
        assert new_experiment.project == experiment.project
        assert new_experiment.user == experiment.user
        assert new_experiment.description == experiment.description
        assert new_experiment.config == experiment.config
        assert new_experiment.declarations == experiment.declarations
        assert new_experiment.code_reference == experiment.code_reference

        # Restart with different declarations and description
        declarations = {
            'lr': 0.1,
            'dropout': 0.5
        }
        description = 'new description'
        new_experiment = experiment.restart(declarations=declarations, description=description)
        assert new_experiment.project == experiment.project
        assert new_experiment.user == experiment.user
        assert new_experiment.description == description
        assert new_experiment.config == experiment.config
        assert new_experiment.declarations == declarations
        assert new_experiment.code_reference == experiment.code_reference

    def test_copy(self):
        experiment = ExperimentFactory()
        new_experiment = experiment.copy()
        assert new_experiment.project == experiment.project
        assert new_experiment.user == experiment.user
        assert new_experiment.description == experiment.description
        assert new_experiment.config == experiment.config
        assert new_experiment.declarations == experiment.declarations
        assert new_experiment.code_reference == experiment.code_reference

        # Restart with different declarations and description
        declarations = {
            'lr': 0.1,
            'dropout': 0.5
        }
        description = 'new description'
        new_experiment = experiment.copy(declarations=declarations, description=description)
        assert new_experiment.project == experiment.project
        assert new_experiment.user == experiment.user
        assert new_experiment.description == description
        assert new_experiment.config == experiment.config
        assert new_experiment.declarations == declarations
        assert new_experiment.code_reference == experiment.code_reference

    def test_resume(self):
        experiment = ExperimentFactory()
        count_experiment = Experiment.objects.count()
        ExperimentStatus.objects.create(experiment=experiment, status=ExperimentLifeCycle.STOPPED)
        assert experiment.last_status == ExperimentLifeCycle.STOPPED

        config = experiment.config
        declarations = experiment.declarations

        # Resume with same config
        experiment.resume()
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.STOPPED
        last_resumed_experiment = experiment.clones.filter(
            cloning_strategy=CloningStrategy.RESUME).last()
        assert last_resumed_experiment.config == config
        assert last_resumed_experiment.declarations == declarations
        assert Experiment.objects.count() == count_experiment + 1
        assert experiment.clones.count() == 1

        # Resume with different config
        new_declarations = {
            'lr': 0.1,
            'dropout': 0.5
        }
        new_experiment = experiment.resume(declarations=new_declarations)
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.STOPPED
        last_resumed_experiment = experiment.clones.filter(
            cloning_strategy=CloningStrategy.RESUME).last()
        assert last_resumed_experiment.config == config
        assert last_resumed_experiment.declarations != declarations
        assert last_resumed_experiment.declarations == new_declarations
        assert Experiment.objects.count() == count_experiment + 2
        assert experiment.clones.count() == 2

        # Resuming a resumed experiment
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            resumed = new_experiment.resume()
            ExperimentStatusFactory(experiment=resumed, status=ExperimentLifeCycle.CREATED)
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.STOPPED
        last_resumed_experiment_new = experiment.clones.filter(
            cloning_strategy=CloningStrategy.RESUME).last()
        assert last_resumed_experiment_new.original_experiment.pk != last_resumed_experiment.pk
        assert (last_resumed_experiment_new.original_experiment.pk ==
                last_resumed_experiment.original_experiment.pk)
        assert last_resumed_experiment.config == config
        assert last_resumed_experiment.declarations != declarations
        assert last_resumed_experiment.declarations == new_declarations
        assert Experiment.objects.count() == count_experiment + 3
        assert experiment.clones.count() == 3

        # Deleting a resumed experiment does not delete other experiments
        last_resumed_experiment_new.set_status(ExperimentLifeCycle.SCHEDULED)
        ExperimentJobFactory(experiment=last_resumed_experiment_new)
        with patch('scheduler.experiment_scheduler.stop_experiment') as mock_stop:
            last_resumed_experiment_new.delete()
        assert experiment.clones.count() == 2
        assert mock_stop.call_count == 1

        # Deleting original experiment deletes all
        with patch('scheduler.experiment_scheduler.stop_experiment') as mock_stop:
            experiment.delete()
        assert Experiment.objects.count() == 0
        assert mock_stop.call_count == 0  # No running experiment

    @patch('scheduler.dockerizer_scheduler.create_build_job')
    def test_non_independent_experiment_creation_doesnt_trigger_start(self, create_build_job):
        build = BuildJobFactory()
        BuildJobStatus.objects.create(status=JobLifeCycle.SUCCEEDED, job=build)
        create_build_job.return_value = build, True, True

        with patch('hpsearch.tasks.hp_create.apply_async') as mock_fct:
            experiment_group = ExperimentGroupFactory()

        assert mock_fct.call_count == 1

        with patch('scheduler.tasks.experiments.experiments_start.apply_async') as mock_fct:
            with patch.object(Experiment, 'set_status') as mock_fct2:
                ExperimentFactory(experiment_group=experiment_group)

        assert mock_fct.call_count == 0
        assert mock_fct2.call_count == 1

    def test_experiment_creation_triggers_status_creation(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            experiment = ExperimentFactory()

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 1
        assert experiment.last_status == ExperimentLifeCycle.CREATED

    def test_independent_experiment_creation_triggers_experiment_scheduling_mocks(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as mock_fct:
            with patch.object(Experiment, 'set_status') as mock_fct2:
                ExperimentFactory()

        assert mock_fct.call_count == 0
        assert mock_fct2.call_count == 1

    def test_independent_experiment_created_status_triggers_experiment_scheduling(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as mock_fct:
            experiment = ExperimentFactory()

        assert mock_fct.call_count == 1
        assert experiment.last_status == ExperimentLifeCycle.CREATED

    def test_independent_experiment_creation_triggers_experiment_scheduling(self):
        content = ExperimentSpecification.read(experiment_spec_content)
        experiment = ExperimentFactory(config=content.parsed_data)
        assert experiment.is_independent is True

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 3
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED,
                                      ExperimentLifeCycle.SCHEDULED,
                                      ExperimentLifeCycle.FAILED]
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.FAILED

    def test_independent_experiment_creation_with_run_triggers_experiment_building(self):
        config = ExperimentSpecification.read(exec_experiment_spec_content)
        # Create a repo for the project
        repo = RepoFactory()

        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as mock_build:
            experiment = ExperimentFactory(config=config.parsed_data, project=repo.project)

        assert mock_build.call_count == 1
        assert experiment.project.repo is not None
        assert experiment.is_independent is True

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 1
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED]

        with patch('scheduler.dockerizer_scheduler.start_dockerizer') as mock_start:
            experiments_build(experiment_id=experiment.id)

        assert mock_start.call_count == 1
        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 2
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED,
                                      ExperimentLifeCycle.BUILDING]
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.BUILDING

    def test_independent_experiment_creation_with_run_triggers_experiment_scheduling(self):
        config = ExperimentSpecification.read(exec_experiment_spec_content)
        # Create a repo for the project
        repo = RepoFactory()

        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as mock_build:
            experiment = ExperimentFactory(config=config.parsed_data, project=repo.project)

        assert mock_build.call_count == 1
        assert experiment.project.repo is not None
        assert experiment.is_independent is True

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 1
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED]

        with patch('scheduler.dockerizer_scheduler.create_build_job') as mock_start:
            build = BuildJobFactory()
            BuildJobStatus.objects.create(status=JobLifeCycle.SUCCEEDED, job=build)
            mock_start.return_value = build, True, True
            experiments_build(experiment_id=experiment.id)

        assert mock_start.call_count == 1
        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 3
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED,
                                      ExperimentLifeCycle.SCHEDULED,
                                      ExperimentLifeCycle.FAILED]
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.FAILED

    @mock.patch('scheduler.experiment_scheduler.ExperimentSpawner')
    def test_create_experiment_with_valid_spec(self, spawner_mock):
        config = ExperimentSpecification.read(experiment_spec_content)

        mock_instance = spawner_mock.return_value
        mock_instance.start_experiment.return_value = start_experiment_value
        mock_instance.job_uuids = {'master': ['fa6203c189a855dd977019854a7ffcc3'],
                                   'worker': ['3a9c9b0bd56b5e9fbdbd1a3d43d57960'],
                                   'ps': ['59e3601232b85a3d8be2511f23a62945']}
        mock_instance.spec = config

        experiment = ExperimentFactory(config=config.parsed_data)
        assert experiment.is_independent is True

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 3
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED,
                                      ExperimentLifeCycle.SCHEDULED,
                                      ExperimentLifeCycle.STARTING]
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.STARTING

        # Assert 1 job was created
        assert ExperimentJob.objects.filter(experiment=experiment).count() == 1
        assert JobResources.objects.count() == 0
        jobs_statuses = ExperimentJob.objects.values_list('statuses__status', flat=True)
        assert set(jobs_statuses) == {JobLifeCycle.CREATED, }
        jobs = ExperimentJob.objects.filter(experiment=experiment)
        assert experiment.calculated_status == ExperimentLifeCycle.STARTING

        for job in jobs:
            # Assert the jobs status is created
            assert job.last_status == JobLifeCycle.CREATED

    @mock.patch('scheduler.experiment_scheduler.TensorflowSpawner')
    def test_create_experiment_with_resources_spec(self, spawner_mock):
        config = ExperimentSpecification.read(exec_experiment_resources_content)
        mock_instance = spawner_mock.return_value
        mock_instance.start_experiment.return_value = start_experiment_value
        mock_instance.job_uuids = {'master': ['fa6203c189a855dd977019854a7ffcc3'],
                                   'worker': ['3a9c9b0bd56b5e9fbdbd1a3d43d57960'],
                                   'ps': ['59e3601232b85a3d8be2511f23a62945']}
        mock_instance.spec = config

        experiment = ExperimentFactory(config=config.parsed_data)
        assert experiment.is_independent is True

        assert ExperimentStatus.objects.filter(experiment=experiment).count() == 3
        assert list(ExperimentStatus.objects.filter(experiment=experiment).values_list(
            'status', flat=True)) == [ExperimentLifeCycle.CREATED,
                                      ExperimentLifeCycle.SCHEDULED,
                                      ExperimentLifeCycle.STARTING]

        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.STARTING

        # Assert 3 jobs were created with resources
        assert ExperimentJob.objects.filter(experiment=experiment).count() == 3
        assert JobResources.objects.count() == 3
        jobs_statuses = ExperimentJob.objects.values_list('statuses__status', flat=True)
        assert set(jobs_statuses) == {JobLifeCycle.CREATED, }
        jobs = ExperimentJob.objects.filter(experiment=experiment)
        assert experiment.calculated_status == ExperimentLifeCycle.STARTING

        for job in jobs:
            # Assert the jobs status is created
            assert job.last_status == JobLifeCycle.CREATED

    @patch('scheduler.tasks.storage.stores_schedule_logs_deletion.apply_async')
    @patch('scheduler.tasks.storage.stores_schedule_outputs_deletion.apply_async')
    def test_delete_experiment_does_not_trigger_experiment_stop_if_not_running(self,
                                                                               delete_outputs_path,
                                                                               delete_logs_path):
        experiment = ExperimentFactory()
        assert delete_outputs_path.call_count == 0
        assert delete_logs_path.call_count == 0
        with patch('scheduler.experiment_scheduler.stop_experiment') as mock_fct:
            experiment.delete()
        assert delete_outputs_path.call_count == 1
        assert delete_logs_path.call_count == 1
        assert mock_fct.call_count == 0

    @patch('scheduler.tasks.storage.stores_schedule_logs_deletion.apply_async')
    @patch('scheduler.tasks.storage.stores_schedule_outputs_deletion.apply_async')
    def test_delete_experiment_triggers_experiment_stop_mocks(self,
                                                              delete_outputs_path,
                                                              delete_logs_path):
        experiment = ExperimentFactory()
        experiment.set_status(ExperimentLifeCycle.SCHEDULED)
        # Add job
        ExperimentJobFactory(experiment=experiment)

        assert delete_outputs_path.call_count == 0
        assert delete_logs_path.call_count == 0
        with patch('scheduler.experiment_scheduler.stop_experiment') as mock_fct:
            experiment.delete()
        assert delete_outputs_path.call_count == 1
        assert delete_logs_path.call_count == 1
        assert mock_fct.call_count == 1

    def test_set_metrics(self):
        config = ExperimentSpecification.read(experiment_spec_content)
        experiment = ExperimentFactory(config=config.parsed_data)
        assert experiment.metrics.count() == 0

        create_at = timezone.now()
        experiments_set_metrics(experiment_id=experiment.id,
                                data={
                                    'created_at': create_at,
                                    'values': {'accuracy': 0.9, 'precision': 0.9}
                                })

        assert experiment.metrics.count() == 1

        experiments_set_metrics(experiment_id=experiment.id,
                                data=[{
                                    'created_at': create_at,
                                    'values': {'accuracy': 0.9, 'precision': 0.9}
                                }, {
                                    'created_at': create_at,
                                    'values': {'accuracy': 0.9, 'precision': 0.9}
                                }])

        assert experiment.metrics.count() == 3

    def test_master_success_influences_other_experiment_workers_status(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            # with patch.object(Experiment, 'set_status') as _:  # noqa
            experiment = ExperimentFactory()

        assert ExperimentLifeCycle.is_done(experiment.last_status) is False
        # Add jobs
        master = ExperimentJobFactory(experiment=experiment, role=TaskType.MASTER)
        assert JobLifeCycle.is_done(master.last_status) is False
        workers = [ExperimentJobFactory(experiment=experiment, role=TaskType.WORKER)
                   for _ in range(2)]
        for worker in workers:
            worker.refresh_from_db()
            assert JobLifeCycle.is_done(worker.last_status) is False

        # Set master to succeeded
        ExperimentJobStatusFactory(job=master, status=JobLifeCycle.SUCCEEDED)

        # All worker should have a success status
        for worker in workers:
            worker.refresh_from_db()
            assert worker.last_status == JobLifeCycle.SUCCEEDED

        # Experiment last status should be success
        experiment.refresh_from_db()
        assert experiment.last_status == ExperimentLifeCycle.SUCCEEDED

    def test_experiments_sync_jobs_statuses(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            with patch.object(Experiment, 'set_status') as _:  # noqa
                experiments = [ExperimentFactory() for _ in range(3)]

        done_xp, no_jobs_xp, xp_with_jobs = experiments

        # Set done status
        with patch('scheduler.experiment_scheduler.stop_experiment') as _:  # noqa
            ExperimentStatusFactory(experiment=done_xp, status=JobLifeCycle.FAILED)

        # Create jobs for xp_with_jobs and update status, and do not update the xp status
        with patch.object(Experiment, 'set_status') as _:  # noqa
            job = ExperimentJobFactory(experiment=xp_with_jobs)
            ExperimentJobStatusFactory(job=job, status=JobLifeCycle.RUNNING)

        xp_with_jobs.refresh_from_db()
        assert xp_with_jobs.last_status is None

        # Mock sync experiments and jobs constants
        with patch('scheduler.tasks.experiments.'
                   'experiments_check_status.apply_async') as check_status_mock:
            experiments_sync_jobs_statuses()

        assert check_status_mock.call_count == 1

        # Call sync experiments and jobs constants
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as build_mock:
            ExperimentStatusFactory(experiment=xp_with_jobs, status=JobLifeCycle.CREATED)
        assert build_mock.call_count == 1
        experiments_sync_jobs_statuses()
        done_xp.refresh_from_db()
        no_jobs_xp.refresh_from_db()
        xp_with_jobs.refresh_from_db()
        assert done_xp.last_status == ExperimentLifeCycle.FAILED
        assert no_jobs_xp.last_status is None
        assert xp_with_jobs.last_status == ExperimentLifeCycle.RUNNING

    def test_copying_an_experiment(self):
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            experiment1 = ExperimentFactory()

        # We create some outputs files for the experiment
        path = stores.create_experiment_outputs_path(
            persistence=experiment1.persistence_outputs,
            experiment_name=experiment1.unique_name)
        open(os.path.join(path, 'file'), 'w+')

        # Create a new experiment that is a clone of the previous
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as _:  # noqa
            experiment2 = ExperimentFactory(original_experiment=experiment1)

        # Check that outputs path for experiment2 does not exist yet
        experiment2_outputs_path = stores.get_experiment_outputs_path(
            persistence=experiment2.persistence_outputs,
            experiment_name=experiment2.unique_name)
        assert os.path.exists(experiment2_outputs_path) is False

        # Handle restart should create the outputs and copy the content of experiment 1
        copy_experiment(experiment2)

        assert os.path.exists(experiment2_outputs_path) is True
        assert os.path.exists(os.path.join(experiment2_outputs_path, 'file')) is True

    def test_managers(self):
        assert isinstance(Experiment.objects, LiveManager)
        assert isinstance(Experiment.archived, ArchivedManager)

    def test_archive(self):
        experiment = ExperimentFactory()
        assert experiment.deleted is False
        assert Experiment.objects.count() == 1
        assert Experiment.all.count() == 1

        experiment.archive()
        assert experiment.deleted is True
        assert Experiment.objects.count() == 0
        assert Experiment.all.count() == 1

        experiment.restore()
        assert experiment.deleted is False
        assert Experiment.objects.count() == 1
        assert Experiment.all.count() == 1


@pytest.mark.experiments_mark
class TestExperimentCommit(BaseViewTest):
    DISABLE_EXECUTOR = False

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory(user=self.auth_client.user)
        self.url = '/{}/{}/{}/repo/upload'.format(API_V1,
                                                  self.project.user.username,
                                                  self.project.name)

    @staticmethod
    def get_upload_file(filename='repo'):
        file = File(open('./tests/fixtures_static/{}.tar.gz'.format(filename), 'rb'))
        return SimpleUploadedFile(filename, file.read(),
                                  content_type='multipart/form-data')

    def create_experiment(self, config):
        config = ExperimentSpecification.read(config)
        return ExperimentFactory(config=config.parsed_data, project=self.project)

    def test_experiment_is_saved_with_commit(self):
        uploaded_file = self.get_upload_file()

        self.auth_client.put(self.url,
                             data={'repo': uploaded_file},
                             content_type=MULTIPART_CONTENT)

        last_commit = self.project.repo.last_commit
        assert last_commit is not None

        # Check experiment is created with commit
        experiment = self.create_experiment(exec_experiment_spec_content)

        assert experiment.code_reference.commit == last_commit[0]
        assert experiment.code_reference.repo == self.project.repo

        # Make a new upload with repo_new.tar.gz containing 2 files
        new_uploaded_file = self.get_upload_file('updated_repo')
        self.auth_client.put(self.url,
                             data={'repo': new_uploaded_file},
                             content_type=MULTIPART_CONTENT)

        new_commit = self.project.repo.last_commit
        assert new_commit is not None
        assert new_commit[0] != last_commit[0]

        # Check new experiment is created with new commit
        new_experiment = self.create_experiment(exec_experiment_spec_content)
        assert new_experiment.code_reference.commit == new_commit[0]
        assert new_experiment.code_reference.repo == self.project.repo

        # Cloning an experiment does not assign commit
        clone_experiment = Experiment.objects.create(
            project=experiment.project,
            user=self.project.user,
            description=experiment.description,
            experiment_group=experiment.experiment_group,
            config=experiment.config,
            original_experiment=experiment,
            code_reference=experiment.code_reference
        )

        assert clone_experiment.code_reference == experiment.code_reference

        # Model experiments should not get a commit
        model_experiment = self.create_experiment(experiment_spec_content)
        assert model_experiment.code_reference is None

    def test_experiment_is_saved_without_code(self):
        # Check experiment is created with commit
        with patch('scheduler.tasks.experiments.experiments_build.apply_async') as mock_fct:
            experiment = self.create_experiment(exec_experiment_ext_repo_spec_content)
        assert mock_fct.call_count == 1

        assert experiment.code_reference is None
