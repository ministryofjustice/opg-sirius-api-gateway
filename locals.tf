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
    "production"  = "sirius-production"
    "development" = "sirius-development"
  }

  vpcs = {
    "production"  = "prod-vpc"
    "development" = "dev-vpc"
  }

  vpc_name = "${lookup(local.vpcs, terraform.workspace)}"

  membrane_hostnames = {
    "production"  = "membrane.production.ecs"
    "development" = "membrane.integration.ecs"
  }

  membrane_hostname = "${lookup(local.membrane_hostnames, terraform.workspace)}"

  target_accounts = {
    "production"  = "649098267436"
    "development" = "288342028542"
  }

  target_account = "${lookup(local.target_accounts, terraform.workspace)}"

  opg_sirius_hosted_zones = {
    "production"  = "sirius.opg.digital"
    "development" = "dev.sirius.opg.digital"
  }

  opg_sirius_hosted_zone = "${lookup(local.opg_sirius_hosted_zones, terraform.workspace)}"

  is_production = {
    "production"  = "true"
    "development" = "false"
  }

  online_lpa_tool_development_api_gateway_allowed_roles = [
    "arn:aws:iam::001780581745:root",
    "arn:aws:iam::050256574573:root", // ecs lpa dev
  ]

  online_lpa_tool_production_api_gateway_allowed_roles = [
    "arn:aws:iam::987830934591:role/preproduction-api-task-role", // ecs lpa preprod
    "arn:aws:iam::980242665824:role/production-api-task-role",    // ecs lpa prod
  ]

  api_gateway_allowed_roles_online_lpa_tool = "${split(",", terraform.workspace == "development" ? join(",", local.online_lpa_tool_development_api_gateway_allowed_roles) : join(",", local.online_lpa_tool_production_api_gateway_allowed_roles))}"

  use_an_lpa_development_api_gateway_allowed_roles = [
    "arn:aws:iam::367815980639:root", // Dev
    "arn:aws:iam::888228022356:root", // Preprod
  ]

  use_an_lpa_production_api_gateway_allowed_roles = [
    "arn:aws:iam::690083044361:root", // Prod
  ]

  api_gateway_allowed_roles_use_an_lpa = "${split(",", terraform.workspace == "development" ? join(",", local.use_an_lpa_development_api_gateway_allowed_roles) : join(",", local.use_an_lpa_production_api_gateway_allowed_roles))}"

  api_gateway_allowed_users = [
    "arn:aws:iam::631181914621:user/andrew.pearce",
    "arn:aws:iam::631181914621:user/neil.smith",
    "arn:aws:iam::631181914621:user/adam.cooper",
    "arn:aws:iam::631181914621:user/richard.mchale",
    "arn:aws:iam::631181914621:user/seema.menon",
    "arn:aws:iam::631181914621:user/gemma.taylor",
    "arn:aws:iam::631181914621:user/pam.crosby",
  ]

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
