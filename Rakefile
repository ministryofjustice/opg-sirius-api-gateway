# frozen_string_literal: true

require 'rake'
namespace :lambda do
  desc 'Lambda: package lambda function'
  task :package do
    sh 'pip3 install -r lambdas/requirements.txt  --target ./lambdas/vendor'
    sh 'cd ./lambdas; zip -r9 ../lambda_artifact.zip .'
    sh 'rm -r ./lambdas/vendor'
  end
  desc 'Lambda: build api tests env file'
  task :buildapitestfile do
    sh 'ruby ./modify_env.rb'
  end
  desc 'Lambda: test lpas collection endpoint'
  task :testlpas do
    Rake::Task['lambda:buildapitestfile'].invoke
    sh 'newman run https://www.getpostman.com/collections/c85538a8e4fb4f19b892 -e /tmp/generated.postman_environment.json'
    sh 'rm /tmp/generated.postman_environment.json'
  end
end

namespace :terraform do
  task :init do
      sh 'terraform init'
  end
  desc 'Terraform: plan'
  task :plan do
    Rake::Task['terraform:init'].invoke
    sh 'terraform workspace select development'
    sh 'terraform plan | ./redact_output.sh'
  end
  desc 'Terraform: apply'
  task :apply do
    Rake::Task['terraform:init'].invoke
    sh 'terraform apply -auto-approve | ./redact_output.sh'
  end
end
