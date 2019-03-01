import requests
import uuid

from hestia.units import to_unit_memory

from django.db.models import Count, Sum

import auditor
import conf

from db.models.clusters import Cluster
from db.models.nodes import ClusterNode
from event_manager.events.cluster import (
    CLUSTER_NODE_CREATED,
    CLUSTER_NODE_DELETED,
    CLUSTER_NODE_UPDATED,
    CLUSTER_RESOURCES_UPDATED,
    CLUSTER_UPDATED
)
from polyaxon.celery_api import celery_app
from polyaxon.settings import CronsCeleryTasks
from polyaxon_k8s.manager import K8SManager


def get_cluster_resources() -> Cluster:
    return Cluster.objects.annotate(
        n_nodes=Count('nodes'),
        n_cpus=Sum('nodes__cpu'),
        memory=Sum('nodes__memory'),
        n_gpus=Sum('nodes__n_gpus')).first()


@celery_app.task(name=CronsCeleryTasks.CLUSTERS_UPDATE_SYSTEM_INFO,
                 time_limit=150,
                 ignore_result=True)
def update_system_info() -> None:
    k8s_manager = K8SManager(in_cluster=True)
    version_api = k8s_manager.get_version()
    cluster = Cluster.load()
    if version_api and cluster.version_api != version_api:
        cluster.version_api = version_api
        cluster.save()
        auditor.record(event_type=CLUSTER_UPDATED,
                       instance=cluster,
                       is_upgrade=conf.get('CHART_IS_UPGRADE'))


@celery_app.task(name=CronsCeleryTasks.CLUSTERS_UPDATE_SYSTEM_NODES,
                 time_limit=150,
                 ignore_result=True)
def update_system_nodes() -> None:
    k8s_manager = K8SManager(in_cluster=True)
    nodes = k8s_manager.list_nodes()
    cluster = Cluster.load()
    nodes_to_update = {}
    nodes_to_create = {node.metadata.name: node for node in nodes}
    deprecated_nodes = []
    for node in cluster.nodes.all():
        if node.name in nodes_to_create:
            nodes_to_update[node.name] = (node, nodes_to_create.pop(node.name))
        else:
            deprecated_nodes.append(node)

    cluster_updated = False
    for node in deprecated_nodes:
        node.is_current = False
        node.save()
        cluster_updated = True
        auditor.record(event_type=CLUSTER_NODE_DELETED, instance=node)

    for node in nodes_to_create.values():
        node_dict = ClusterNode.from_node_item(node)
        node_dict['cluster'] = cluster
        instance = ClusterNode.objects.create(**node_dict)
        cluster_updated = True
        auditor.record(event_type=CLUSTER_NODE_CREATED, instance=instance)

    for current_node, new_node in nodes_to_update.values():
        node_dict = ClusterNode.from_node_item(new_node)
        node_updated = False
        for k, v in node_dict.items():
            if v != getattr(current_node, k):
                setattr(current_node, k, v)
                node_updated = True
            if not current_node.is_current:
                current_node.is_current = True
                node_updated = True
        if node_updated:
            current_node.save()
            cluster_updated = True
            auditor.record(event_type=CLUSTER_NODE_UPDATED, instance=current_node)

    if cluster_updated:
        cluster = get_cluster_resources()
        auditor.record(event_type=CLUSTER_RESOURCES_UPDATED,
                       instance=cluster,
                       n_nodes=cluster.n_nodes,
                       memory=round(cluster.memory / (1000 ** 3), 2),
                       n_cpus=cluster.n_cpus,
                       n_gpus=cluster.n_gpus)


@celery_app.task(name=CronsCeleryTasks.CLUSTERS_NODES_NOTIFICATION_ALIVE,
                 time_limits=60,
                 ignore_result=True)
def cluster_nodes_analytics() -> None:
    cluster = get_cluster_resources()
    notification = uuid.uuid4()
    notification_url = conf.get('POLYAXON_NOTIFICATION_CLUSTER_NODES_URL').format(
        url=conf.get('CLUSTER_NOTIFICATION_URL'),
        cluster_uuid=cluster.uuid.hex,
        n_nodes=cluster.n_nodes,
        n_cpus=cluster.n_cpus,
        memory=to_unit_memory(cluster.memory or 0),
        n_gpus=cluster.n_gpus,
        notification=notification,
        version=conf.get('CHART_VERSION'))
    try:
        requests.get(notification_url)
    except requests.RequestException:
        pass
