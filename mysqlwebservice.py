from constructs import Construct
from cdk8s import Names

from imports import k8s

class MysqlWebService(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        image: str,
        replicas=1,
        port=3306,
        container_port=3306,
        **kwargs
    ):
        super().__init__(scope, id)

        label = {"app": Names.to_label_value(self)}

        config_map = k8s.KubeConfigMap(
            self,
            'mysql-config-map',
            data={
                'MYSQL_DATABASE':       'mysqldb',
                'MYSQL_USER':           'mysqldb-user',
                'MYSQL_PASSWORD':       'mysqldb-secret',
                'MYSQL_ROOT_PASSWORD':  'mysqldb-root-secret',
            }
        )

        k8s.KubePersistentVolumeClaim(
            self,
            'pvc',
            metadata=k8s.ObjectMeta(name='mysql-persistent-storage'),
            spec=k8s.PersistentVolumeClaimSpec(
                access_modes=['ReadWriteOnce'],
                resources=k8s.ResourceRequirements(
                    requests={
                        'storage': k8s.Quantity.from_string("10Gi"),
                    },
                ),
                storage_class_name="rawfile-btrfs"
            ),
        )

        container = k8s.Container(
            name='mysql',
            image=image,
            env_from=[
                k8s.EnvFromSource(
                    config_map_ref=k8s.ConfigMapEnvSource(
                        name=config_map.name,
                    ),
                ),
            ],
            ports=[
                k8s.ContainerPort(container_port=3306),
            ],
            resources=k8s.ResourceRequirements(
                limits={
                    "cpu": k8s.Quantity.from_string("200m"),
                    "memory": k8s.Quantity.from_string("550Mi"),
                },
                requests={
                    "cpu": k8s.Quantity.from_string("100m"),
                    "memory": k8s.Quantity.from_string("200Mi"),
                },
            ),
            volume_mounts=[
                k8s.VolumeMount(name='mysql-data', mount_path='/var/lib/mysql'),
            ],
        )

        k8s.KubeStatefulSet(
            self,
            'mysql',
            metadata=k8s.ObjectMeta(name='mysql'),
            spec=k8s.StatefulSetSpec(
                service_name='mysql',
                replicas=replicas,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label),
                    spec=k8s.PodSpec(
                        containers=[container],
                        volumes=[
                            k8s.Volume(
                                name="mysql-data",
                                persistent_volume_claim=k8s.PersistentVolumeClaimVolumeSource(
                                    claim_name="mysql-persistent-storage"
                                ),
                            )
                        ],
                    ),
                ),
            ),
        )

        k8s.KubeService(
            self,
            "service",
            metadata=k8s.ObjectMeta(name="mysql"),
            spec=k8s.ServiceSpec(
                type="ClusterIP",
                ports=[
                    k8s.ServicePort(
                        port=port,
                        target_port=k8s.IntOrString.from_number(container_port),
                    )
                ],
                selector=label,
            ),
        )
