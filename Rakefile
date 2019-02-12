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
  desc 'Workstation: plan'
  task :plan do
    Rake::Task['terraform:init'].invoke
    sh 'terraform plan | landscape'
  end
  desc 'Workstation: apply'
  task :apply do
    Rake::Task['terraform:init'].invoke
    sh 'terraform apply -var-file config.json -var-file versions.tfvars -auto-approve'
    Rake::Task['terraform:clean_local_files'].invoke
  end
  desc 'Workstation: clean_local_files'
  task :clean_local_files do
    sh 'terraform state rm local_file.api_migration'
    sh 'terraform state rm local_file.membrane_migration'
    sh 'terraform state rm local_file.smoke_tests_task'
  end
end

#ave identity -- bundle exec rake terraform:init
