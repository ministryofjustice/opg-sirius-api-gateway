# opg-sirius-api-gateway
OPG API Gateway into Sirius: Managed by opg-org-infra &amp; Terraform


## Running Terraform Locally

This repository comes with an `.envrc` file containing useful environment variables for working with this repository.

`.envrc` can be sourced automatically using either [direnv](https://direnv.net) or manually with bash.

```bash
source .envrc
```

```bash
direnv allow
```

## AWS Credentials Setup

See [opg-org-infra/AWS-CONSOLE.md](https://github.com/ministryofjustice/opg-org-infra/blob/master/AWS-CONSOLE.md) for setup instructions.

### Initialize Terraform

shared  357766484745
```bash
aws-vault exec identity -- terraform init -backend-config="role_arn=arn:aws:iam::311462405659:role/management-admin"
```

Then you can run terraform commands

```bash
aws-vault exec identity -- terraform $command
```

All commands should now work through the identity account.

For example import a resource using the following command

```bash
aws-vault exec identity -- terraform import module.opg-backoffice-datastore-preprod2.aws_s3_bucket.bucket opg-backoffice-datastore-preprod2
```
