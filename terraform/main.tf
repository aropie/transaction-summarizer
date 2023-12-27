locals {
  lambda_src_dir           = "${path.module}/dir_to_src"
  lambda_function_zip_path = "${path.module}/lambda/lambda-function.zip"
}

resource "null_resource" "pip_install" {
  triggers = {
    shell_hash = "${sha256(file("${path.module}/../requirements.txt"))}"
  }

  provisioner "local-exec" {
    command = "python3 -m pip install -r ../requirements.txt -t ${path.module}/lambda/layer/python"
  }
}

data "archive_file" "layer" {
  type             = "zip"
  source_dir       = "${path.module}/lambda/layer"
  output_path      = "${path.module}/lambda/layer.zip"
  output_file_mode = "777"
  depends_on       = [null_resource.pip_install]
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = "pkg-layer"
  filename            = data.archive_file.layer.output_path
  source_code_hash    = data.archive_file.layer.output_base64sha256
  compatible_runtimes = ["python3.10", "python3.9", "python3.8"]
}

data "archive_file" "code" {
  type             = "zip"
  source_dir       = local.lambda_src_dir
  output_path      = local.lambda_function_zip_path
  output_file_mode = "777"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-iam-role"

  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

resource "aws_iam_policy" "policy" {

  name   = "lambda-policy"
  policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:PutLogEvents"
     ],
     "Resource": "arn:aws:logs:*:*:*",
     "Effect": "Allow"
   },
   {
     "Action": [
       "s3:ListBucket"
    ],
    "Resource": "*",
    "Effect": "Allow"
   }

 ]
}
EOF
}

# Attach the AWSLambdaBasicExecutionRole policy to the IAM role
resource "aws_iam_role_policy_attachment" "lambda_role_policy" {
  policy_arn = aws_iam_policy.policy.arn
  role       = aws_iam_role.lambda_role.name
}

resource "aws_lambda_function" "lambda" {
  function_name    = "transaction-summarizer"
  handler          = "src.app.handle"
  runtime          = "python3.9"
  filename         = data.archive_file.code.output_path
  source_code_hash = data.archive_file.code.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  layers           = [aws_lambda_layer_version.layer.arn]
  environment {
    variables = {
      "TARG" = "Terraform sends its regards"
    }
  }
}





# Config for S3 Bucket
# resource "aws_s3_bucket" "transactions-store" {
#   bucket        = "transactions-store"
#   force_destroy = true
# }

# resource "aws_s3_bucket_ownership_controls" "bucket-ownership" {
#   bucket = aws_s3_bucket.transactions-store.id

#   rule {
#     object_ownership = "BucketOwnerPreferred"
#   }
# }

# resource "aws_s3_bucket_public_access_block" "access-block" {
#   bucket = aws_s3_bucket.transactions-store.id

#   block_public_acls       = false
#   block_public_policy     = false
#   ignore_public_acls      = false
#   restrict_public_buckets = false
# }

# resource "aws_s3_bucket_acl" "bucket-acl" {
#   depends_on = [
#     aws_s3_bucket_ownership_controls.bucket-ownership,
#     aws_s3_bucket_public_access_block.access-block,
#   ]

#   bucket = aws_s3_bucket.transactions-store.id
#   acl    = "public-read-write"
# }

# resource "aws_s3_bucket_public_access_block" "transactions-store" {
#   bucket = aws_s3_bucket.transactions-store.id

#   block_public_acls   = false
#   block_public_policy = false
# }


# resource "aws_iam_policy" "iam_policy" {

#   name        = "aws_iam_policy_for_terraform_aws_lambda_role"
#   description = "AWS IAM Policy for managing aws lambda role"
#   policy      = <<EOF
# {
#   "Version":"2012-10-17",
#   "Statement":[
#     {
#       "Sid":"AddPerm",
#       "Effect":"Allow",
#       "Principal": "*",
#       "Action":["s3:GetObject"],
#       "Resource":["arn:aws:s3:::examplebucket/*"]
#     }
#   ]
# }
# EOF
# }

# Setup API Gateway

resource "aws_api_gateway_rest_api" "TransactionSummarizerAPI" {
  name = "TransactionSummarizerAPI"
}

resource "aws_api_gateway_resource" "TransactionSummarizerAPI" {
  parent_id   = aws_api_gateway_rest_api.TransactionSummarizerAPI.root_resource_id
  path_part   = "upload"
  rest_api_id = aws_api_gateway_rest_api.TransactionSummarizerAPI.id
}

resource "aws_api_gateway_method" "TransactionSummarizerAPI" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.TransactionSummarizerAPI.id
  rest_api_id   = aws_api_gateway_rest_api.TransactionSummarizerAPI.id
}

resource "aws_api_gateway_integration" "TransactionSummarizerAPI" {
  http_method             = aws_api_gateway_method.TransactionSummarizerAPI.http_method
  resource_id             = aws_api_gateway_resource.TransactionSummarizerAPI.id
  rest_api_id             = aws_api_gateway_rest_api.TransactionSummarizerAPI.id
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda.invoke_arn
}


# Method Response and Enabling CORS

resource "aws_api_gateway_method_response" "TransactionSummarizerAPI" {
  rest_api_id = aws_api_gateway_rest_api.TransactionSummarizerAPI.id
  resource_id = aws_api_gateway_resource.TransactionSummarizerAPI.id
  http_method = aws_api_gateway_method.TransactionSummarizerAPI.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true,
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true
  }

}

resource "aws_api_gateway_deployment" "TransactionSummarizerAPI" {
  rest_api_id = aws_api_gateway_rest_api.TransactionSummarizerAPI.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.TransactionSummarizerAPI.id,
      aws_api_gateway_method.TransactionSummarizerAPI.id,
      aws_api_gateway_integration.TransactionSummarizerAPI.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.TransactionSummarizerAPI.id
  rest_api_id   = aws_api_gateway_rest_api.TransactionSummarizerAPI.id
  stage_name    = "prod"
}

# Permission for API Gateway to invoke lambda function
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${var.aws_account_id}:${aws_api_gateway_rest_api.TransactionSummarizerAPI.id}/*/${aws_api_gateway_method.TransactionSummarizerAPI.http_method}${aws_api_gateway_resource.TransactionSummarizerAPI.path}"
}
