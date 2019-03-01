import json
import logging
import re
import requests

from typing import Any, Dict, List, Mapping, Optional

import docker

from docker.errors import DockerException, NotFound

import conf
import polyaxon_gpustat

from constants.containers import ContainerStatuses
from db.models.nodes import ClusterNode, NodeGPU
from db.redis.containers import RedisJobContainers
from db.redis.to_stream import RedisToStream
from schemas.containers import ContainerResourcesConfig

logger = logging.getLogger('polyaxon.monitors.resources')

try:
    docker_client = docker.from_env(version="auto", timeout=10)
except DockerException:
    docker_client = None


def get_gpu_resources() -> Any:
    try:
        return polyaxon_gpustat.query()
    except:  # noqa
        return []


def get_container_gpu_indices(container: Any) -> List[int]:
    gpus = []
    devices = container.attrs['HostConfig']['Devices']
    for dev in devices:
        match = re.match(r'/dev/nvidia(?P<index>[0-9]+)', dev['PathOnHost'])
        if match:
            gpus.append(int(match.group('index')))
    return gpus


def get_container(containers: Dict, container_id: str) -> Any:
    if not docker_client:
        return None
    try:  # we check first that the container is visible in this node
        container = docker_client.containers.get(container_id)
    except NotFound:
        logger.debug("container `%s` was not found", container_id)
        return None

    if container_id in containers:
        return containers[container_id]

    if container.status != ContainerStatuses.RUNNING:
        return None

    containers[container_id] = container
    return container


def get_container_resources(node: 'ClusterNode',
                            container: Any,
                            gpu_resources: Mapping) -> Optional['ContainerResourcesConfig']:
    # Check if the container is running
    if container.status != ContainerStatuses.RUNNING:
        logger.debug("`%s` container is not running", container.name)
        RedisJobContainers.remove_container(container.id)
        return

    job_uuid, experiment_uuid = RedisJobContainers.get_job(container.id)

    if not job_uuid:
        logger.debug("`%s` container is not recognised", container.name)
        return

    logger.debug(
        "Streaming resources for container %s in (job, experiment) (`%s`, `%s`) ",
        container.id, job_uuid, experiment_uuid)

    try:
        stats = container.stats(decode=True, stream=False)
    except json.decoder.JSONDecodeError:
        logger.info("Error streaming states for `%s`", container.name)
        return
    except NotFound:
        logger.debug("`%s` was not found", container.name)
        RedisJobContainers.remove_container(container.id)
        return
    except requests.ReadTimeout:
        return

    precpu_stats = stats['precpu_stats']
    cpu_stats = stats['cpu_stats']

    pre_total_usage = float(precpu_stats['cpu_usage']['total_usage'])
    total_usage = float(cpu_stats['cpu_usage']['total_usage'])
    delta_total_usage = total_usage - pre_total_usage

    pre_system_cpu_usage = float(precpu_stats['system_cpu_usage'])
    system_cpu_usage = float(cpu_stats['system_cpu_usage'])
    delta_system_cpu_usage = system_cpu_usage - pre_system_cpu_usage

    percpu_usage = cpu_stats['cpu_usage']['percpu_usage']
    num_cpu_cores = len(percpu_usage)
    if num_cpu_cores >= node.cpu * 1.5:
        logger.warning('Docker reporting num cpus `%s` and kubernetes reporting `%s`',
                       num_cpu_cores, node.cpu)
        num_cpu_cores = node.cpu
    cpu_percentage = 0.
    percpu_percentage = [0.] * num_cpu_cores
    if delta_total_usage > 0 and delta_system_cpu_usage > 0:
        cpu_percentage = (delta_total_usage / delta_system_cpu_usage) * num_cpu_cores * 100.0
        percpu_percentage = [cpu_usage / total_usage * cpu_percentage for cpu_usage in percpu_usage]

    memory_used = int(stats['memory_stats']['usage'])
    memory_limit = int(stats['memory_stats']['limit'])

    container_gpu_resources = None
    if gpu_resources:
        gpu_indices = get_container_gpu_indices(container)
        container_gpu_resources = [gpu_resources[gpu_indice] for gpu_indice in gpu_indices]

    return ContainerResourcesConfig.from_dict({
        'job_uuid': job_uuid,
        'job_name': job_uuid,  # it will be updated during the streaming
        'experiment_uuid': experiment_uuid,
        'container_id': container.id,
        'cpu_percentage': cpu_percentage,
        'n_cpus': num_cpu_cores,
        'percpu_percentage': percpu_percentage,
        'memory_used': memory_used,
        'memory_limit': memory_limit,
        'gpu_resources': container_gpu_resources
    })


def update_cluster_node(node_gpus: Dict) -> None:
    if not node_gpus:
        return
    node = ClusterNode.objects.filter(name=conf.get('K8S_NODE_NAME')).first()
    for node_gpu_index in node_gpus.keys():
        node_gpu_value = node_gpus[node_gpu_index]
        try:
            node_gpu = NodeGPU.objects.get(cluster_node=node, index=node_gpu_index)
        except NodeGPU.DoesNotExist:
            node_gpu = NodeGPU(cluster_node=node, index=node_gpu_index)
        node_gpu.serial = node_gpu_value['serial']
        node_gpu.name = node_gpu_value['name']
        node_gpu.memory = node_gpu_value['memory_total']
        node_gpu.save()


def run(containers: Dict, node: 'ClusterNode', persist: bool) -> None:
    container_ids = RedisJobContainers.get_containers()
    gpu_resources = get_gpu_resources()
    if gpu_resources:
        gpu_resources = {gpu_resource['index']: gpu_resource for gpu_resource in gpu_resources}
    update_cluster_node(gpu_resources)
    for container_id in container_ids:
        container = get_container(containers, container_id)
        if not container:
            continue
        try:
            payload = get_container_resources(node, containers[container_id], gpu_resources)
        except KeyError:
            payload = None
        if payload:
            payload = payload.to_dict()
            # todo: Re-enable publishing
            # logger.debug("Publishing resources event")
            # celery_app.send_task(
            #     K8SEventsCeleryTasks.K8S_EVENTS_HANDLE_RESOURCES,
            #     kwargs={'payload': payload, 'persist': persist})

            job_uuid = payload['job_uuid']
            # Check if we should stream the payload
            # Check if we have this container already in place
            experiment_uuid = RedisJobContainers.get_experiment_for_job(job_uuid)
            set_last_resources_cond = (
                RedisToStream.is_monitored_job_resources(job_uuid) or
                RedisToStream.is_monitored_experiment_resources(experiment_uuid))
            if set_last_resources_cond:
                RedisToStream.set_latest_job_resources(job_uuid, payload)
