
resource "aws_dynamodb_table" "auth_cache" {
  name          = "opg-gateway-cache-auth"
  billing_mode  = "PAY_PER_REQUEST"

  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
}
