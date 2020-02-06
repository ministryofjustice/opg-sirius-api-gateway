// Identifies all clients that can talk to the Membrane ELB

resource "aws_security_group" "lambda" {
  name        = "opg-sirius-api-gateway-lambdas"
  description = "egress rules for OPG Sirius API Gateway"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_security_group" "lambda" {
  tags {
    Name = "integration-lambda-membrane-access-${local.target_environment}"
  }
  filter {
    name = "tag:Name"
    values = ["integration-lambda-membrane-access-${local.target_environment}"]
  }
}
