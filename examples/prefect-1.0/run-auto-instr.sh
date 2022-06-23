# opentelemetry-bootstrap -a install
# opentelemetry-instrument --traces_exporter console flask run

# Run Python script with automatic instrumentation
opentelemetry-instrument --traces_exporter console python base.py