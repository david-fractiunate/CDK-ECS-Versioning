#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from infra.infra_stack import InfraStack


env=core.Environment(account='123456789012', region='eu-central-1')

app = core.App()
InfraStack(app, "WorkflowEcsVersioningStack", "Demo-Service", env)
    
app.synth()
