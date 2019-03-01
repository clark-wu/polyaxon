from django.db.models import Q

from constants.jobs import JobLifeCycle
from db.models.projects import Project
from libs.base_clean import BaseCleanCommand
from scheduler import notebook_scheduler, tensorboard_scheduler


class Command(BaseCleanCommand):
    @staticmethod
    def _clean() -> None:
        filters = Q(tensorboard_jobs=None) | Q(notebook_jobs=None)
        for project in Project.objects.exclude(filters):
            if project.has_notebook:
                notebook_scheduler.stop_notebook(
                    project_name=project.unique_name,
                    project_uuid=project.uuid.hex,
                    notebook_job_name=project.notebook.unique_name,
                    notebook_job_uuid=project.notebook.uuid.hex)
                project.notebook.set_status(status=JobLifeCycle.STOPPED,
                                            message='Stop triggered by the cleaning hook.')
            if project.has_tensorboard:
                tensorboard_scheduler.stop_tensorboard(
                    project_name=project.unique_name,
                    project_uuid=project.uuid.hex,
                    tensorboard_job_name=project.tensorboard.unique_name,
                    tensorboard_job_uuid=project.tensorboard.uuid.hex)
                project.tensorboard.set_status(status=JobLifeCycle.STOPPED,
                                               message='Stop triggered by the cleaning hook.')
