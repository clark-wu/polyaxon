import os

import pytest

import stores

from factories.factory_experiment_groups import ExperimentGroupFactory
from factories.factory_experiments import ExperimentFactory
from scheduler.tasks.storage import stores_schedule_logs_deletion, stores_schedule_outputs_deletion
from tests.utils import BaseTest


@pytest.mark.paths_mark
class TestExperimentGroupPaths(BaseTest):
    def setUp(self):
        super().setUp()
        self.experiment_group = ExperimentGroupFactory()
        self.project = self.experiment_group.project

    def test_experiment_group_logs_path_creation_deletion(self):
        experiment = ExperimentFactory(user=self.project.user,
                                       project=self.project,
                                       experiment_group=self.experiment_group)
        experiment_logs_path = stores.get_experiment_logs_path(
            experiment_name=experiment.unique_name,
            temp=False)
        stores.create_experiment_logs_path(experiment_name=experiment.unique_name, temp=False)
        open(experiment_logs_path, '+w')
        experiment_group_logs_path = stores.get_experiment_group_logs_path(
            experiment_group_name=self.experiment_group.unique_name)
        # Should be true, created by the signal
        assert os.path.exists(experiment_logs_path) is True
        assert os.path.exists(experiment_group_logs_path) is True
        stores_schedule_logs_deletion(persistence=None, subpath=self.experiment_group.subpath)
        assert os.path.exists(experiment_logs_path) is False
        assert os.path.exists(experiment_group_logs_path) is False

    def test_experiment_group_outputs_path_creation_deletion(self):
        experiment = ExperimentFactory(user=self.project.user,
                                       project=self.project,
                                       experiment_group=self.experiment_group)
        stores.create_experiment_outputs_path(
            persistence=experiment.persistence_outputs,
            experiment_name=experiment.unique_name)
        experiment_outputs_path = stores.get_experiment_outputs_path(
            persistence=experiment.persistence_outputs,
            experiment_name=experiment.unique_name)
        experiment_group_outputs_path = stores.get_experiment_group_outputs_path(
            persistence=self.experiment_group.persistence_outputs,
            experiment_group_name=self.experiment_group.unique_name)
        assert os.path.exists(experiment_outputs_path) is True
        assert os.path.exists(experiment_group_outputs_path) is True
        stores_schedule_outputs_deletion(persistence='outputs',
                                         subpath=self.experiment_group.subpath)
        assert os.path.exists(experiment_outputs_path) is False
        assert os.path.exists(experiment_group_outputs_path) is False
