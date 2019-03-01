import logging

from constants.pipelines import OperationStatuses, PipelineStatuses
from pipelines import dags
from pipelines.utils import (
    get_operation_run,
    get_pipeline_run,
    skip_operation_runs_for_pipeline_run,
    stop_operation_runs_for_pipeline_run
)
from polyaxon.celery_api import celery_app
from polyaxon.settings import Intervals, PipelinesCeleryTasks

_logger = logging.getLogger(__name__)


@celery_app.task(name=PipelinesCeleryTasks.PIPELINES_START,
                 bind=True,
                 max_retries=None,
                 ignore_result=True)
def pipelines_start(self: 'celery_app.task', pipeline_run_id: int) -> None:
    pipeline_run = get_pipeline_run(pipeline_run_id=pipeline_run_id)
    if not pipeline_run:
        _logger.info('Pipeline `%s` does not exist any more.', pipeline_run_id)

    pipeline_run.on_schedule()
    dag, op_runs = pipeline_run.dag
    sorted_ops = dags.sort_topologically(dag=dag)
    op_runs_to_start = [op_runs[op_run_id] for op_run_id in sorted_ops
                        if op_runs[op_run_id].last_status == OperationStatuses.CREATED]
    concurrency = pipeline_run.pipeline.n_operation_runs_to_start
    future_check = False
    while op_runs_to_start and concurrency > 0:
        op_run = op_runs_to_start.pop()
        if op_run.schedule_start():
            # If we end up here it means that the task
            future_check = True
        else:
            concurrency -= 1

    if op_runs_to_start or future_check:
        # Schedule another task
        self.retry(countdown=Intervals.PIPELINES_SCHEDULER)


@celery_app.task(name=PipelinesCeleryTasks.PIPELINES_START_OPERATION, ignore_result=True)
def pipelines_start_operation(operation_run_id: int) -> None:
    operation_run = get_operation_run(operation_run_id=operation_run_id)
    if not operation_run:
        _logger.info('Operation `%s` does not exist any more.', operation_run_id)

    operation_run.schedule_start()


@celery_app.task(name=PipelinesCeleryTasks.PIPELINES_STOP_OPERATIONS, ignore_result=True)
def pipelines_stop_operations(pipeline_run_id: int, message: str = None) -> None:
    pipeline_run = get_pipeline_run(pipeline_run_id=pipeline_run_id)
    if not pipeline_run:
        _logger.info('Pipeline `%s` does not exist any more.', pipeline_run_id)

    stop_operation_runs_for_pipeline_run(pipeline_run, message=message)


@celery_app.task(name=PipelinesCeleryTasks.PIPELINES_SKIP_OPERATIONS, ignore_result=True)
def pipelines_skip_operations(pipeline_run_id: int, message: str = None) -> None:
    pipeline_run = get_pipeline_run(pipeline_run_id=pipeline_run_id)
    if not pipeline_run:
        _logger.info('Pipeline `%s` does not exist any more.', pipeline_run_id)

    # We stop all op runs first
    stop_operation_runs_for_pipeline_run(pipeline_run, message=message)
    # Then we marked them as skipped
    skip_operation_runs_for_pipeline_run(pipeline_run, message=message)


@celery_app.task(name=PipelinesCeleryTasks.PIPELINES_CHECK_STATUSES, ignore_result=True)
def pipelines_check_statuses(pipeline_run_id: int, status: str, message: str = None) -> None:
    pipeline_run = get_pipeline_run(pipeline_run_id=pipeline_run_id)
    if not pipeline_run:
        _logger.info('Pipeline `%s` does not exist any more.', pipeline_run_id)

    if status in OperationStatuses.DONE_STATUS:
        status = PipelineStatuses.FINISHED
    pipeline_run.set_status(status=status, message=message)
