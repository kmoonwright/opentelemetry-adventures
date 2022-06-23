terraform {
  required_providers {
    honeycombio = {
      source = "honeycombio/honeycombio"
      version = "~> 0.3.0"
    }
  }
}

variable "dataset" {
  type = string
}

variable "app_version" {
  type = string
}

resource "honeycombio_marker" "marker" {
  message = "deploy ${var.app_version}"
  type    = "deploy"
  url     = "https://www.honeycomb.io/"
  dataset = var.dataset
}