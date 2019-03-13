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

## Rakefile
A Rakefile has been provided to ensure that the commands you run on your machine are the same as those run by the pipeline.

They are effectively shortcuts, intended to be useful, and not an abstraction or obfuscation of the work.

You can list the available commands in the Rake file

```bash
bundle exec rake -T
rake lambda:package       # Workstation: package-lambda
rake terraform:apply      # Workstation: apply
rake terraform:localplan  # Workstation: localplan
rake terraform:plan       # Workstation: plan
```

For commands that require aws IAM roles, you can use aws-vault to select the correct profile
(see https://github.com/ministryofjustice/opg-new-starter/blob/master/AWS-VAULT.md)

```bash
aws-vault exec identity -- bundle exec rake terraform:localplan
```


