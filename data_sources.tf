data "aws_region" "current" {}

data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Stack"
    values = ["${local.vpc_name}"]
  }
}
