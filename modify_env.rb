#!/usr/bin/ruby
require 'json'
require 'aws-sdk-core'
require_relative 'file_loader'

CONFIG       = hash_from_file('config.json')
ROLE_NAME    = ENV['TF_VAR_api_test_role'] || 'ci'
TF_WORKSPACE = ENV['TF_WORKSPACE'] || 'development'
ACCOUNT_ID   = CONFIG['accounts'][TF_WORKSPACE]
ENDPOINT_DOMAIN_NAME   = CONFIG['endpoint_domain_name'][TF_WORKSPACE]

resp = Aws::STS::Resource.new(
  region: 'eu-west-1'
).client.assume_role(
  role_arn: "arn:aws:iam::#{ACCOUNT_ID}:role/#{ROLE_NAME}",
  role_session_name: 'checkdeployment'
)

obj = hash_from_file('./tests/template.postman_environment.json')

session = { 
  "aws_access_key_id" => resp.credentials.access_key_id,
  "aws_secret_access_key" => resp.credentials.secret_access_key,
  "aws_session_token" => resp.credentials.session_token,
  "endpoint_domain_name" => ENDPOINT_DOMAIN_NAME,
}

obj["values"].map { | x | x["value"] = session[ x["key"] ] }
 
File.open("/tmp/generated.postman_environment.json", "w") { |file| file.puts JSON.pretty_generate(obj)}
