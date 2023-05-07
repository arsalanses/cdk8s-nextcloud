from constructs import Construct
from cdk8s import Names

from imports import k8s

class NextcloudWebService(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        image: str,
        replicas=1,
        port=80,
        container_port=8080,
        **kwargs
    ):
        super().__init__(scope, id)

        label = {"app": Names.to_label_value(self)}

        config_map = k8s.KubeConfigMap(
            self,
            'nextcloud-config-map',
            data={
                'nextcloud_admin_user':     'admin',
                'nextcloud_admin_password': 'secret',
                'MYSQL_HOST':               'mysql',
                'MYSQL_DATABASE':           'nextclouddb',
                'MYSQL_USER':               'nextclouddb-user',
                'MYSQL_PASSWORD':           'nextclouddb-secret'
            }
        )

        container = k8s.Container(
            name="nextcloud",
            image=image,
            env_from=[
                k8s.EnvFromSource(
                    config_map_ref=k8s.ConfigMapEnvSource(
                        name=config_map.name,
                    ),
                ),
            ],
            ports=[
                k8s.ContainerPort(container_port=container_port)
            ],
            resources=k8s.ResourceRequirements(
                limits={
                    "cpu": k8s.Quantity.from_string("200m"),
                    "memory": k8s.Quantity.from_string("250Mi"),
                },
                requests={
                    "cpu": k8s.Quantity.from_string("100m"),
                    "memory": k8s.Quantity.from_string("100Mi"),
                },
            ),
            # liveness_probe=k8s.Probe(
            #     http_get=k8s.HttpGetAction(
            #         path='/index.php',
            #         port=k8s.IntOrString.from_number(80)
            #     ),
            #     initial_delay_seconds=60,
            #     period_seconds=10,
            # ),
            # readiness_probe=k8s.Probe(
            #     http_get=k8s.HttpGetAction(
            #         path='/index.php',
            #         port=k8s.IntOrString.from_number(80)
            #     ),
            #     initial_delay_seconds=10,
            #     period_seconds=5,
            # ),
        )

        k8s.KubeDeployment(
            self,
            "deployment",
            spec=k8s.DeploymentSpec(
                replicas=replicas,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label),
                    spec=k8s.PodSpec(
                        containers=[container],
                    ),
                ),
            ),
        )

        k8s.KubeService(
            self,
            "service",
            metadata=k8s.ObjectMeta(name="nextcloud"),
            spec=k8s.ServiceSpec(
                type="LoadBalancer",
                ports=[
                    k8s.ServicePort(
                        port=port,
                        target_port=k8s.IntOrString.from_number(container_port),
                    )
                ],
                selector=label,
            ),
        )
