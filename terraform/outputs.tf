output "thing_name" {
  value = aws_iot_thing.my_thing.name
}

output "policy_arn" {
  value = aws_iot_policy.my_thing_policy[count.index].arn
}

output "device_certificate_pem" {
  value     = aws_iot_certificate.my_thing_cert.certificate_pem
  sensitive = true
}

output "device_private_key" {
  value     = aws_iot_certificate.my_thing_cert.private_key
  sensitive = true
}

output "iot_endpoint" {
  value = data.aws_iot_endpoint.iot_endpoint.endpoint_address
}
