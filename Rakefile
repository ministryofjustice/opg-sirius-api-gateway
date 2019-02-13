# frozen_string_literal: true

require 'rake'

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
    sh 'terraform plan'
  end
  desc 'Workstation: plan'
  task :plan do
    Rake::Task['terraform:init'].invoke
    sh 'terraform plan | landscape'
  end
  desc 'Workstation: apply'
  task :apply do
    Rake::Task['terraform:init'].invoke
    sh 'terraform apply -auto-approve'
  end
end
