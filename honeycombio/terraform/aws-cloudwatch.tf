module "cloudwatch_metric_stream_with_excludes" {
  source = "honeycombio/honeycomb-cloudwatch-metric-stream/aws"

  name                   = "cms_with_excludes"
  honeycomb_dataset_name = "cloudwatch-with-excludes"
  honeycomb_api_key = "XXXXXXXXXXXXXXXXXXXXXX"

  namespace_exclude_filters = ["AWS/RDS", "AWS/ELB"]
}



