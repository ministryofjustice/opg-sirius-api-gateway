
resource "aws_dynamodb_table" "auth_cache" {
  name          = "opg-gateway-cache-auth"
  billing_mode  = "PAY_PER_REQUEST"

  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = "${local.default_tags}"
}

resource "aws_dynamodb_table" "data_cache" {
  name          = "opg-gateway-cache-data"
  billing_mode  = "PAY_PER_REQUEST"

  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = "expires"
    enabled = true
  }

  tags = "${local.default_tags}"
}
