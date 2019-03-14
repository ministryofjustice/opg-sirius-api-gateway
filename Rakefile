# frozen_string_literal: true

require 'rake'
namespace :lambda do
  desc 'Workstation: package-lambda'
  task :package do
    sh 'pip3 install -r lambdas/requirements.txt  --target ./lambdas/vendor'
    sh 'cd ./lambdas; zip -r9 ./lpas_collection_lambda.zip .'
    sh 'rm -r ./lambdas/vendor'
  end
  desc 'Workstation: test_lpas_collection'
  task :testlpas do
    sh 'newman run https://www.getpostman.com/collections/de1229e9f4d76fd28379'
  end
end

namespace :terraform do
  task :init do
    if ENV['CI']
      sh 'terraform init'
    else
      sh 'terraform init -backend-config="role_arn=arn:aws:iam::311462405659:role/management-admin"'
    end
  end
  desc 'Workstation: localplan'
  task :localplan do
    Rake::Task['terraform:init'].invoke
    sh 'terraform workspace select development'
    sh 'terraform plan | ./redact_output.sh'
  end
  desc 'Workstation: plan'
  task :plan do
    Rake::Task['terraform:init'].invoke
    sh 'terraform plan | landscape'
  end
  desc 'Workstation: apply'
  task :apply do
    Rake::Task['terraform:init'].invoke
    sh 'terraform apply -auto-approve | ./redact_output.sh'
  end
  desc 'Workstation: apply'
  task :apply do
    Rake::Task['terraform:init'].invoke
    sh 'terraform apply -auto-approve | ./redact_output.sh'
  end
end
