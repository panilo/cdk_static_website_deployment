import os
from os import path

from aws_cdk import CfnOutput, Environment, RemovalPolicy, Stack
from aws_cdk import aws_s3 as s3
from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_cloudfront import (
    BehaviorOptions,
    Distribution,
    OriginAccessIdentity,
    ViewerProtocolPolicy,
)
from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_s3 import BucketAccessControl, BucketEncryption
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct


class WebsiteStack(Stack):
    def __init__(
        self, scope: Construct, domain: str, tls_certificate: Certificate, website_assets_path: str, **kwargs
    ) -> None:
        cdk_environment = Environment(
            region="eu-west-1", account=os.getenv("CDK_DEFAULT_ACCOUNT")
        )

        super().__init__(
            scope,
            f"WebsiteDeploy-{domain.replace('.', '-')}",
            env=cdk_environment,
            cross_region_references=True,
            **kwargs,
        )

        domains = [domain, f"www.{domain}"]

        website_bucket = s3.Bucket(
            self,
            "website_bucket",
            access_control=BucketAccessControl.PRIVATE,
            encryption=BucketEncryption.S3_MANAGED,
        )

        website_bucket.apply_removal_policy(RemovalPolicy.DESTROY)

        BucketDeployment(
            self,
            "website_deployment",
            destination_bucket=website_bucket,
            sources=[Source.asset(website_assets_path)],
        )

        oai = OriginAccessIdentity(self, "origin_access_identity")
        oai.apply_removal_policy(RemovalPolicy.DESTROY)

        website_bucket.grant_read(identity=oai)

        distribution = Distribution(
            self,
            "website_distribution",
            default_root_object="index.html",
            default_behavior=BehaviorOptions(
                origin=S3Origin(website_bucket, origin_access_identity=oai),
                viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=domains,
            certificate=tls_certificate,
        )

        CfnOutput(
            self,
            "distribution_url",
            value=distribution.domain_name,
            export_name=f"DistributionDomainName-{domain.replace('.', '-')}",
        )

        CfnOutput(
            self,
            "bucket_arn",
            value=website_bucket.bucket_arn,
            export_name=f"WebsiteBuckerARN-{domain.replace('.', '-')}",
        )
