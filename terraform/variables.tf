variable "thing_short_name" {
  type        = string
  description = "Name of the AWS IoT Thing to create"
  default     = "TerraformThing"
}

variable "thing_name_prefix" {
  type        = string
  description = "Prefix attached to thing name, used for SQS client filtering"
  default     = "Lamp-"
}

variable "iot_policy_name" {
  type        = string
  description = "Name of the AWS IoT policy to create and attach to the Thing"
  default     = "lamp_policy"
}

variable "region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "account_id" {
  type        = string
  description = "AWS account ID"
}

variable "thing_group_name" {
  type    = string
  default = "Pi_Lamps"
}

variable "sns_topic" {
  type    = string
  default = "test/lamp"
}

variable "environment" {
  type        = string
  description = "Used for tagging infrastructure"
}
