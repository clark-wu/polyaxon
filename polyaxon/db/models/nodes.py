import uuid

from typing import Dict

from hestia.unknown import UNKNOWN

from django.contrib.postgres.fields import JSONField
from django.db import models

import conf

from constants.nodes import NodeLifeCycle, NodeRoles
from db.models.utils import DiffModel, SequenceModel


class NodeParser(object):

    @staticmethod
    def get_status(node) -> str:
        status = [c.status for c in node.status.conditions if c.type == 'Ready'][0]
        if status == 'True':
            return NodeLifeCycle.READY
        if status == 'FALSE':
            return NodeLifeCycle.NOT_READY
        return NodeLifeCycle.UNKNOWN

    @staticmethod
    def get_n_gpus(node) -> int:
        return int(node.status.allocatable.get(conf.get('K8S_GPU_RESOURCE_KEY'), 0))

    @staticmethod
    def get_cpu(node) -> float:
        cpu = node.status.allocatable['cpu']
        if cpu.lower()[-1] == 'm':
            cpu = int(cpu[:-1]) / 1000
        return float(cpu)

    @staticmethod
    def to_bytes(size_str: str) -> int:
        try:
            return int(float(size_str))
        except (ValueError, TypeError):
            pass

        fixed_point_unit_multiplier = {
            'k': 1000,
            'm': 1000 ** 2,
            'g': 1000 ** 3,
            't': 1000 ** 4
        }

        power_two_unit_multiplier = {
            'ki': 1024,
            'mi': 1024 ** 2,
            'gi': 1024 ** 3,
            'ti': 1024 ** 4
        }

        if size_str[-2:].lower() in power_two_unit_multiplier.keys():
            return int(size_str[:-2]) * power_two_unit_multiplier.get(size_str[-2:].lower(), 1)

        if size_str[-1].lower() in fixed_point_unit_multiplier.keys():
            return int(size_str[:-1]) * fixed_point_unit_multiplier.get(size_str[-1].lower(), 1)

        return 0

    @classmethod
    def get_memory(cls, node) -> int:
        return cls.to_bytes(node.status.allocatable['memory'])

    @staticmethod
    def is_master(node) -> bool:
        if ('node-role.kubernetes.io/master' in node.metadata.labels or
                node.metadata.labels.get('kubernetes.io/role') == NodeRoles.MASTER or
                node.metadata.labels.get('kubernetes.io/hostname') == 'minikube'):
            return True
        return False

    @classmethod
    def get_role(cls, node) -> str:
        return NodeRoles.MASTER if cls.is_master(node) else NodeRoles.AGENT

    @staticmethod
    def get_docker_version(node) -> str:
        cri = node.status.node_info.container_runtime_version
        return cri[len('docker://'):] if cri.startswith('docker://') else UNKNOWN

    @staticmethod
    def is_schedulable(node) -> bool:
        if not node.spec.taints:
            return True

        for t in node.spec.taints:
            if t.key == 'node-role.kubernetes.io/master' and t.effect == 'NoSchedule':
                return False

        return True

    @staticmethod
    def get_schedulable_state(node) -> bool:
        return not node.spec.unschedulable

    @staticmethod
    def get_hostname(node) -> str:
        for a in node.status.addresses:
            if a.type == 'Hostname':
                return a.address


class ClusterNode(SequenceModel):
    """A model that represents the cluster node."""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=False)
    name = models.CharField(
        max_length=256,
        null=False,
        help_text='Name of the node')
    cluster = models.ForeignKey(
        'db.Cluster',
        on_delete=models.CASCADE,
        related_name='nodes')
    hostname = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    role = models.CharField(
        max_length=16,
        choices=NodeRoles.CHOICES,
        help_text='The role of the node')
    docker_version = models.CharField(
        max_length=128,
        blank=True,
        null=True)
    kubelet_version = models.CharField(
        max_length=64)
    os_image = models.CharField(max_length=128)
    kernel_version = models.CharField(max_length=128)
    schedulable_taints = models.BooleanField(default=False)
    schedulable_state = models.BooleanField(default=False)
    memory = models.BigIntegerField()
    cpu = models.FloatField()
    n_gpus = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=24,
        default=NodeLifeCycle.UNKNOWN,
        choices=NodeLifeCycle.CHOICES)
    is_current = models.BooleanField(default=True)

    class Meta:
        app_label = 'db'
        unique_together = (('cluster', 'sequence'),)

    def __str__(self):
        return '{}/{}'.format(self.cluster, self.name)

    def save(self, *args, **kwargs):  # pylint:disable=arguments-differ
        filter_query = ClusterNode.sequence_objects.filter(cluster=self.cluster)
        self._set_sequence(filter_query=filter_query)
        super().save(*args, **kwargs)

    @classmethod
    def from_node_item(cls, node) -> Dict:
        return {
            'name': node.metadata.name,
            'hostname': NodeParser.get_hostname(node),
            'role': NodeParser.get_role(node),
            'docker_version': NodeParser.get_docker_version(node),
            'kubelet_version': node.status.node_info.kubelet_version,
            'os_image': node.status.node_info.os_image,
            'kernel_version': node.status.node_info.kernel_version,
            'schedulable_taints': NodeParser.is_schedulable(node),
            'schedulable_state': NodeParser.get_schedulable_state(node),
            'memory': NodeParser.get_memory(node),
            'cpu': NodeParser.get_cpu(node),
            'n_gpus': NodeParser.get_n_gpus(node),
            'status': NodeParser.get_status(node)}


class NodeGPU(DiffModel):
    """A model that represents the node's gpu."""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=False)
    index = models.PositiveSmallIntegerField()
    serial = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    name = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    memory = models.BigIntegerField(
        default=0,
        blank=True,
        null=True)
    cluster_node = models.ForeignKey(
        'db.ClusterNode',
        on_delete=models.CASCADE,
        related_name='gpus')

    class Meta:
        app_label = 'db'
        ordering = ['index']
        unique_together = (('cluster_node', 'index'),)

    def __str__(self) -> str:
        return self.serial


class ClusterEvent(models.Model):
    """A model to catch all errors and warning events of the cluster."""
    cluster = models.ForeignKey(
        'db.Cluster',
        on_delete=models.CASCADE,
        related_name='events')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    data = JSONField()
    meta = JSONField()
    level = models.CharField(max_length=16)

    class Meta:
        app_label = 'db'

    def __str__(self) -> str:
        return 'Event {} at {}'.format(self.level, self.created_at)
