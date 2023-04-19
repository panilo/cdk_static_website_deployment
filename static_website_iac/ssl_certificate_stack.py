import os

from aws_cdk import Environment, Stack
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation
from aws_cdk.aws_route53 import HostedZone
from constructs import Construct


class SSLCertificateStack(Stack):
    def __init__(self, scope: Construct, domain: str, **kwargs) -> None:
        cdk_environment = Environment(
            region="us-east-1", account=os.getenv("CDK_DEFAULT_ACCOUNT")
        )
        super().__init__(
            scope,
            f"SSLCertificateStack-{domain.replace('.', '-')}",
            env=cdk_environment,
            cross_region_references=True,
            **kwargs,
        )

        website_hosted_zone = HostedZone.from_lookup(
            self, "domain_hosted_zone", domain_name=domain
        )

        self.certificate = Certificate(
            self,
            "website_certificate",
            domain_name=domain,
            subject_alternative_names=[f"www.{domain}"],
            validation=CertificateValidation.from_dns(website_hosted_zone),
        )
