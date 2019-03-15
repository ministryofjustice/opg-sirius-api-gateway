#!/usr/bin/ruby
require 'json'
require 'aws-sdk-core'
require_relative 'file_loader'

CONFIG       = hash_from_file('config.json')
ROLE_NAME    = ENV['TF_VAR_api_test_role'] || 'ci'
TF_WORKSPACE = ENV['TF_WORKSPACE'] || 'development'
ACCOUNT_ID   = CONFIG['accounts'][TF_WORKSPACE]

resp = Aws::STS::Resource.new(
  region: 'eu-west-1'
).client.assume_role(
  role_arn: "arn:aws:iam::#{ACCOUNT_ID}:role/#{ROLE_NAME}",
  role_session_name: 'checkdeployment'
)

json = File.read('./tests/template.postman_environment.json')
obj = JSON.parse(json)

obj["values"][0]["value"] = resp.credentials.access_key_id
obj["values"][1]["value"] = resp.credentials.secret_access_key
obj["values"][2]["value"] = resp.credentials.session_token

File.open("./tests/generated.postman_environment.json", "w") { |file| file.puts JSON.pretty_generate(obj)}
