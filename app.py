#!/usr/bin/env python3
import os 

import aws_cdk as cdk
from static_website_iac.ssl_certificate_stack import SSLCertificateStack
from static_website_iac.website_stack import WebsiteStack


website_assets_path = os.getenv("WEBSITE_PATH")
website_main_domain = os.getenv("WEBSITE_DOMAIN")

app = cdk.App()

certificate_stack = SSLCertificateStack(app, website_main_domain)
WebsiteStack(app, website_main_domain, certificate_stack.certificate, website_assets_path)

app.synth()