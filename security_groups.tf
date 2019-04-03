
// Identifies all clients that can talk to the Membrane ELB
data "aws_security_group" "membrane_client" {
  name = "${local.membrane_client_security_group_name}"
}

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
