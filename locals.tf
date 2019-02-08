locals {
  accounts = {
    "opg-sirius-production"  = "649098267436"
    "opg-sirius-development" = "288342028542"
    "lpa-production"         = "550790013665"
    "lpa-development"        = "001780581745"
    "digideps-production"    = "515688267891"
    "digideps-development"   = "248804316466"
    "refunds-production"     = "574983609246"
    "refunds-development"    = "792093328875"
    "opg-backups"            = "238302996107"
    "opg-shared"             = "357766484745"
    "sandbox"                = "995199299616"
    "sirius-development"     = "653761790766"
    "sirius-production"      = "313879017102"
    "management"             = "311462405659"
    "digicop-production"     = "933639921819"
    "digicop-preproduction"  = "540070264006"
    "digicop-development"    = "705467933182"
  }

  trusted_account = {
    name = "OPG Shared"
    id   = "${lookup(local.accounts, "opg-shared")}"
  }

  account_name = "development"

  account_tags = {
    is_production    = "${local.account_name == "production" ? "true" : "false"}"
    environment_name = "${local.account_name}"
  }

  default_tags = {
    # this account is also managed by Ansible right now.
    # Terraform              = ""
    business-unit = "OPG"

    application            = "sirius"
    is-production          = "${local.account_tags["is_production"]}"
    environment-name       = "${local.account_tags["environment_name"]}"
    owner                  = "OPGOPS opgteam@digital.justice.gov.uk"
    infrastructure-support = "OPGOPS opgteam@digital.justice.gov.uk"
    runbook                = "https://github.com/ministryofjustice/opg-webops-runbooks/tree/master/Sirius"
    source-code            = "https://gitlab.service.opg.digital/opsforks/opg-core-deploy"
    Environment            = "${local.account_name}"
    Project                = "core"
    Stack                  = "dev-vpc"
    component              = ""
  }
}
