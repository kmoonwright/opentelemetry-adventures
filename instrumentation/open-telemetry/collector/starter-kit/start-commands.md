# Once we have the deployment ready, we can make a call to its /orders endpoint and it will generate a few spans for us. The easiest way to make this call for testing is by doing a port-forward, so that calls to localhost:8080/orders will land at our application in the Kubernetes cluster:

kubectl port-forward deployment/myapp 8080
...
Forwarding from 127.0.0.1:8080 -> 8080

# Let’s now tail the logs for our collector: once we make a call to our service, the loggingexporter in the collector will make sure to record this event in the logs.

kubectl logs deployments/opentelemetrycollector -f
...
2021-01-22T12:59:53.561Z info service/service.go:267 Everything is ready. Begin running and processing data.

# And finally, let’s generate some spans:

curl localhost:8080/order
...
Created