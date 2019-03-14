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

  account_names = {
    "production"    = "sirius-production"
    "preproduction" = "sirius-production"
    "development"   = "sirius-development"
  }

  vpcs = {
    "production"    = "prod-vpc"
    "preproduction" = "prod-vpc"
    "development"   = "dev-vpc"
  }

  vpc_name = "${lookup(local.vpcs, terraform.workspace)}"

  target_accounts = {
    "production"    = "649098267436"
    "preproduction" = "649098267436"
    "development"   = "288342028542"
  }

  target_account = "${lookup(local.target_accounts, terraform.workspace)}"

  opg_sirius_hosted_zones = {
    "production"    = "sirius.opg.digital"
    "preproduction" = "sirius.opg.digital"
    "development"   = "dev.sirius.opg.digital"
  }

  opg_sirius_hosted_zone = "${lookup(local.opg_sirius_hosted_zones, terraform.workspace)}"

  is_production = {
    "production"    = "true"
    "preproduction" = "false"
    "development"   = "false"
  }

  default_tags = {
    business-unit          = "OPG"
    application            = "Sirius"
    is-production          = "${lookup(local.is_production, terraform.workspace)}"
    environment-name       = "${lookup(local.account_names, terraform.workspace)}"
    owner                  = "OPGOPS opgteam@digital.justice.gov.uk"
    infrastructure-support = "OPGOPS opgteam@digital.justice.gov.uk"
    runbook                = "https://github.com/ministryofjustice/opg-webops-runbooks/tree/master/Sirius"
    source-code            = "https://github.com/ministryofjustice/opg-sirius-api-gateway"
    Environment            = "${lookup(local.account_names, terraform.workspace)}"
    Project                = "core"
    Stack                  = "${local.vpc_name}"
    component              = "OPG Sirius API Gateway"
  }
}
