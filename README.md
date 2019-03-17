# opg-sirius-api-gateway
OPG API Gateway into Sirius: Managed by opg-org-infra &amp; Terraform

## Project build status - production
[![CircleCI](https://circleci.com/gh/ministryofjustice/opg-sirius-api-gateway/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/opg-sirius-api-gateway/tree/master)


## Working localling with Terraform

### Setting Env Vars

This repository comes with an `.envrc` file containing useful environment variables for working with this repository.

`.envrc` can be sourced automatically using either [direnv](https://direnv.net) or manually with bash.

```bash
source .envrc
```
or
```bash
direnv allow
```

### AWS Credentials Setup
You will need an AWS user that has write permissions into the accounts you want to work with
See [opg-org-infra/AWS-CONSOLE.md](https://github.com/ministryofjustice/opg-org-infra/blob/master/AWS-CONSOLE.md) for credentials setup instructions.
And also [opg-new-starter/AWS-VAULT.md](https://github.com/ministryofjustice/opg-new-starter/blob/master/AWS-VAULT.md)

### Initialize Terraform

```bash
aws-vault exec identity -- terraform init -backend-config="role_arn=arn:aws:iam::311462405659:role/management-admin"
```

Then you can run terraform commands

```bash
aws-vault exec identity -- terraform $command
```

All commands through an identity account.

For example, import a resource using the following command

```bash
aws-vault exec identity -- terraform import module.any-bucket-you-own.aws_s3_bucket.bucket any-bucket-you-own
```

## Rakefile - Shortcuts for local work
A Rakefile has been provided with commands helpful for local work.

They are effectively shortcuts, intended to be useful.

Some are used in the CI pipeline too.

### Set up your environment
Make sure you have Ruby installed
```bash
ruby -v
```

If you need help installing ruby, see here. https://www.ruby-lang.org/en/documentation/installation/

install the bundler gem
```bash
gem install bundler
```

Now install the gems required for the package
```bash
bundle install
```


### Listing the available Rake tasks
You can list the available commands in the Rake file

```bash
bundle exec rake -T
rake lambda:buildapitestfile  # Lambda: build api tests env file
rake lambda:package           # Lambda: package lambda function
rake lambda:testlpas          # Lambda: test lpas collection endpoint
rake terraform:apply          # Terraform: apply
rake terraform:plan           # Terraform: plan
```


### Running a Rake task
For commands that require aws IAM roles, you can use aws-vault to select the correct profile
(see https://github.com/ministryofjustice/opg-new-starter/blob/master/AWS-VAULT.md)

```bash
aws-vault exec identity -- bundle exec rake terraform:localplan
```


## Testing the OPG Sirius API Gateway

Testing of the deployed api gateway is done using Postman and Newman

https://www.getpostman.com/downloads/
https://www.npmjs.com/package/newman

Install Newman
```bash
npm install -g newman
```

Run a test against development
```bash
aws-vault exec identity -- bundle exec rake lambda:testlpas
```
