locals {
  accounts = {
    "opg-sirius-production"  = "649098267436"
    "opg-sirius-development" = "288342028542"
    "lpa-production"         = "550790013665"
    "lpa-development"        = "001780581745"
    "sandbox"                = "995199299616"
    "sirius-development"     = "653761790766"
    "sirius-production"      = "313879017102"
    "management"             = "311462405659"
  }

  account_name = "sirius-development"

  vpc = {
    "production"    = "prod-vpc"
    "preproduction" = "prod-vpc"
    "development"   = "dev-vpc"
  }

  target_account = {
    "production"    = "649098267436"
    "preproduction" = "649098267436"
    "development"   = "288342028542"
  }

  account_tags = {
    is_production    = "${local.account_name == "sirius-production" ? "true" : "false"}"
    environment_name = "${local.account_name}"
  }

  default_tags = {
    business-unit          = "OPG"
    application            = "sirius"
    is-production          = "${local.account_tags["is_production"]}"
    environment-name       = "${local.account_tags["environment_name"]}"
    owner                  = "OPGOPS opgteam@digital.justice.gov.uk"
    infrastructure-support = "OPGOPS opgteam@digital.justice.gov.uk"
    runbook                = "https://github.com/ministryofjustice/opg-webops-runbooks/tree/master/Sirius"
    source-code            = "https://github.com/ministryofjustice/opg-sirius-api-gateway"
    Environment            = "${local.account_name}"
    Project                = "core"
    Stack                  = "${lookup(local.vpc, terraform.workspace )}"
    component              = "OPG Sirius API Gateway"
  }
}
