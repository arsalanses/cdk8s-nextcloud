#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart

# from imports import k8s
from nextcloudwebservice import NextcloudWebService
from mysqlwebservice import MysqlWebService

class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # define resources here
        
        NextcloudWebService(self, 'nextcloud', image='nextcloud:latest', port=27015, container_port=80, replicas=2)
        MysqlWebService(self, 'mysql', image='mysql:8.0-debian', replicas=1)

app = App()
MyChart(app, "cdk8s-nextcloud")

app.synth()
