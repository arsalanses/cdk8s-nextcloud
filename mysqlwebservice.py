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
        port=80,
        container_port=3306,
        **kwargs
    ):
        super().__init__(scope, id)

        label = {"app": Names.to_label_value(self)}

        k8s.KubeDeployment(
            self,
            "deployment",
            spec=k8s.DeploymentSpec(
                replicas=replicas,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label),
                    spec=k8s.PodSpec(
                        containers=[
                            k8s.Container(
                                name="mysql",
                                image=image,
                                ports=[
                                    k8s.ContainerPort(container_port=container_port)
                                ],
                                env=[
                                    k8s.EnvVar(
                                        name='MYSQL_DATABASE',
                                        value='nextclouddb'
                                    ),
                                    k8s.EnvVar(
                                        name='MYSQL_USER',
                                        value='nextclouddb-user'
                                    ),
                                    k8s.EnvVar(
                                        name='MYSQL_PASSWORD',
                                        value='nextclouddb-secret'
                                    ),
                                    k8s.EnvVar(
                                        name='MYSQL_ROOT_PASSWORD',
                                        value='nextclouddb-root-secret'
                                    )
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
                            )
                        ],
                        volumes=[
                            k8s.Volume(
                                name="mysql-data",
                                persistent_volume_claim=k8s.PersistentVolumeClaimVolumeSource(
                                    claim_name="mysql-pvc"
                                ),
                            )
                        ]
                    ),
                ),
            ),
        )

        k8s.KubePersistentVolumeClaim(
            self,
            "pvc",
            metadata=k8s.ObjectMeta(name="mysql-pvc"),
            spec=k8s.PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=k8s.ResourceRequirements(
                    requests={"storage": k8s.Quantity.from_string("2Gi")}
                ),
                storage_class_name="rawfile-btrfs"
            )
        )
