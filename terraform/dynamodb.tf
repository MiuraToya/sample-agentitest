resource "aws_dynamodb_table" "todos" {
  name         = "${var.project_name}-todos"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "N"
  }
}
