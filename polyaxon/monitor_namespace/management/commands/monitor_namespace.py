import time

from typing import Optional

from kubernetes.client.rest import ApiException

from django.db import InterfaceError, OperationalError, ProgrammingError

import conf

from db.models.clusters import Cluster
from libs.base_monitor import BaseMonitorCommand
from monitor_namespace import monitor
from polyaxon_k8s.manager import K8SManager


class Command(BaseMonitorCommand):
    help = 'Watch namespace warning and errors events.'

    def get_cluster_or_wait(self, log_sleep_interval: int) -> Optional['Cluster']:
        max_trials = 10
        trials = 0
        while trials < max_trials:
            try:
                return Cluster.load()
            except (InterfaceError, ProgrammingError, OperationalError) as e:
                monitor.logger.exception("Database is not synced yet %s\n", e)
                trials += 1
                time.sleep(log_sleep_interval * 2)
        return None

    def handle(self, *args, **options) -> None:
        log_sleep_interval = options['log_sleep_interval']
        self.stdout.write(
            "Started a new namespace monitor with, "
            "log sleep interval: `{}`.".format(log_sleep_interval),
            ending='\n')
        k8s_manager = K8SManager(namespace=conf.get('K8S_NAMESPACE'), in_cluster=True)
        cluster = self.get_cluster_or_wait(log_sleep_interval)
        if not cluster:
            # End process
            return

        while True:
            try:
                monitor.run(k8s_manager, cluster)
            except ApiException as e:
                monitor.logger.error(
                    "Exception when calling CoreV1Api->list_event_for_all_namespaces: %s\n", e)
                time.sleep(log_sleep_interval)
            except ValueError as e:
                monitor.logger.error(
                    "Exception when calling CoreV1Api->list_event_for_all_namespaces: %s\n", e)
            except Exception as e:
                monitor.logger.exception("Unhandled exception occurred: %s\n", e)
