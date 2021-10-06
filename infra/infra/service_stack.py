from aws_cdk import core as cdk

class WorkflowEcsVersioningStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, service_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        stage_name = "dev"
        cluster_name = "test"
        domain_name = ""
        load_balancer_name=f"{service_name}-lb"
        self.ecr_repository_name = service_name
        self.docker_asset_name = "latest" if self.node.try_get_context("IMAGE_TAG") is None else self.node.try_get_context("IMAGE_TAG")


#       VPC

#       ECR
        ecr_repository = ecr.Repository.from_repository_name(self, "ECRRepository", self.ecr_repository_name)

#       Time to trigger Container Update w latest
        dt = datetime.now()
        dt = dt.replace(tzinfo=timezone.utc)

task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
        image=ecs.ContainerImage.from_ecr_repository(ecr_repository, tag=self.docker_asset_name),
        container_name='personalized-images',
        container_port=9500,
        enable_logging=True,
        environment={
          'SPRING_PROFILES_ACTIVE': stage_name,
        #   'SPRING_APPLICATION_NAME': self.spring_application_name,
          'CLOUD_AWS_STACK_NAME': self.stack_name,
          'CLOUD_AWS_REGION_STATIC': self.region,
          'AWS_REGION': self.region,
          'rebuild_trigger': str(dt)
        },
        secrets={
          'TODO': ecs.Secret.from_secrets_manager(secret, 'secret_item_key')
        },
        task_role=task_role,
        log_driver=ecs.LogDriver.aws_logs(
            stream_prefix=service_name,
            log_group=logs.LogGroup(
                self,
                "LogGroup",
                log_group_name=service_name,
                retention=logs.RetentionDays(logs.RetentionDays.THREE_MONTHS) 
            ),
        ),
    )

    
    alb = elb.ApplicationLoadBalancer(self, 'ApplicationLoadBalancer', vpc=vpc, internet_facing=True, load_balancer_name=load_balancer_name)
    service_cluster = ecs.Cluster(self, 'Cluster', cluster_name=cluster_name, vpc=vpc)
    dummy_service = ecs_patterns.ApplicationLoadBalancedFargateService(
        self,
        'Service',
        certificate=certificatemanager.Certificate(
            self,
            "Certificate",
            domain_name=f'{service_name}.{domain_name}',
            validation_method=certificatemanager.ValidationMethod.DNS
        ),
        cluster=service_cluster,
        domain_name=f'{service_name}.{domain_name}',
        domain_zone=route53.HostedZone.from_lookup(self, 'HostedZone', domain_name=domain_name, private_zone=False),
        load_balancer=alb,
        health_check_grace_period=core.Duration.minutes(10),
        protocol=elb.ApplicationProtocol.HTTPS,
        public_load_balancer=True,
        task_image_options=task_image_options,
        cpu=256,
        memory_limit_mib=512
    )

    dummy_service.target_group.configure_health_check(path='/health')

    self.service = dummy_service.service
