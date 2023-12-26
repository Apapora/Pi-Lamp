resource "aws_iot_thing" "my_thing" {
  name = local.thing_full_name
  attributes = {
    terraform   = "true"
    environment = var.environment
  }
}

data "aws_iot_endpoint" "iot_endpoint" {
  endpoint_type = "iot:Data-ATS"
}

data "aws_iam_policy" "existing_iot_policy" {
  name = var.iot_policy_name
}

resource "aws_iot_policy" "my_thing_policy" {
  count = data.aws_iam_policy.existing_iot_policy.arn ? 0 : 1
  name  = var.iot_policy_name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "iot:Publish",
          "iot:Receive"
        ],
        "Resource" : "arn:aws:iot:${var.region}:${var.account_id}:topic/${var.sns_topic}"
      },
      {
        "Effect" : "Allow",
        "Action" : "iot:Subscribe",
        "Resource" : "arn:aws:iot:${var.region}:${var.account_id}:topicfilter/${var.sns_topic}"
      },
      {
        "Effect" : "Allow",
        "Action" : "iot:Connect",
        "Resource" : [
          "arn:aws:iot:${var.region}:${var.account_id}:client/${var.thing_name_prefix}*"
        ]
      }
    ]
  })
}

resource "aws_iot_certificate" "my_thing_cert" {
  active = true
}

resource "aws_iot_policy_attachment" "my_thing_poly_att" {
  count  = data.aws_iam_policy.existing_iot_policy.arn ? 0 : 1
  policy = aws_iot_policy.my_thing_policy.name
  target = aws_iot_certificate.my_thing_cert.arn
}
