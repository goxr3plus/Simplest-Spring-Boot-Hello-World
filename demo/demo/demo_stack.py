from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_logs,

    aws_sns as sns,
    aws_ecs_patterns as ecsp,
    aws_lambda,
    aws_cloudwatch as cloudwatch,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import Duration
from aws_cdk.aws_sns_subscriptions import EmailSubscription, EmailSubscriptionProps
from aws_cdk.aws_cloudwatch_actions import SnsAction
import aws_cdk.aws_cloudwatch_actions as cw_actions

from aws_cdk.aws_logs import CfnSubscriptionFilter
import aws_cdk.aws_logs_destinations as destinations


class DemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "DemoQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # bucket = s3.Bucket(self, "MyFirstBucket", versioned=True)
        #
        # ecr_repository = ecr.Repository(self, "ecs-devops-repository", repository_name="ecs-devops-repository")
        # vpc
        vpc = ec2.Vpc(self, 'CICD',
                      cidr='192.168.50.0/24',
                      max_azs=2,
                      enable_dns_hostnames=True,
                      enable_dns_support=True,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              name='PUBLIC-Subnet1',
                              subnet_type=ec2.SubnetType.PUBLIC,
                              cidr_mask=26
                          ),
                          ec2.SubnetConfiguration(
                              name='Private-Subnet2',
                              subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                              cidr_mask=26
                          )
                      ],
                      nat_gateways=1
                      )
        # cluster
        cluster = ecs.Cluster(self, "CICDCluster", vpc=vpc)
        # log
        log_group = aws_logs.LogGroup(
            self,
            "ecs-ccid-service-logs-groups",
            log_group_name="ecs-cicd-service-logs",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # aws_ecs_patterns
        # ecs.ContainerImage.from_asset("server/") 需要本地电脑mac的docker进行编译
        # service
        ecsp.ApplicationLoadBalancedFargateService(self, "CICDFargateService",
                                                   cluster=cluster,
                                                   # cpu=5,
                                                   desired_count=2,
                                                   task_image_options=ecsp.ApplicationLoadBalancedTaskImageOptions(
                                                       # image=ecs.ContainerImage.from_asset("server/")#
                                                       container_port=8080,
                                                       image=ecs.ContainerImage.from_registry(
                                                           "gbsnaker/simplest-spring-boot-hello-world"),
                                                       log_driver=ecs.LogDrivers.aws_logs(
                                                           stream_prefix="CICDFargateService",
                                                           log_group=log_group)
                                                   ),
                                                   memory_limit_mib=512,
                                                   public_load_balancer=True,
                                                   # assign_public_ip=True
                                                   )

        mf = aws_logs.MetricFilter(self, "INFOLOGfilter",
                                   log_group=log_group,
                                   metric_namespace="MYAPP",
                                   metric_name="myinfolog",
                                   # filter_pattern=aws_logs.FilterPattern.any_term("INFO"),
                                   filter_pattern=aws_logs.FilterPattern.any_term("ERROR"),
                                   metric_value="1"
                                   )

        # expose a metric from the metric filter
        metric = mf.metric(
            period=Duration.minutes(5),
            statistic="sum",
            unit=cloudwatch.Unit("COUNT")
        )

        # topic sns
        my_topic = sns.Topic(self, "CICDTOPIC")
        my_topic.add_subscription(EmailSubscription("longmenkezhai@gmail.com"))

        alarm = cloudwatch.Alarm(self, "CidAlarm",
                                 metric=metric,
                                 threshold=2,
                                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                                 evaluation_periods=1,
                                 actions_enabled=True
                                 )
        alarm.add_alarm_action(cw_actions.SnsAction(my_topic))
