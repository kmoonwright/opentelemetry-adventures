# 1
# Manual Instrumentation - "Starting point"

This is the starting point for all the examples. It consists of a service that will return a random year between 
2015 and 2020. The service is duplicated in Java and Go for this workshop.

When launched either service will listen on port `6001` for the `/year` endpoint.

## Go
The Go service is built using the [gorilla/mux](https://github.com/gorilla/mux) package for request routing.


# 1.1
# Manual Instrumentation

Manual instrumentation is adding attributes to existing spans, and creating new spans (or traces) to better understand 
our code.

## Go
Auto-instrumentation for a Go service requires code to be added to the service's startup. Once added, spans will be
emitted for instrumented frameworks (ie: gorilla/mux). Traces emitted can be extending with additional attributes to
existing spans and/or new spans.

Go requires to explicitly pass context for manual instrumentation. Span context is stored in the general context as a value.
You can get access to the current span from that context with `trace.SpanFromContext(ctx)`.


# 2
# Asynchronous - "Starting Point"

This marks the starting point to instrument and understand asynchronous operations in a service. Here services have a new
asynchronous operation added. That operation is also instrumented, but the spans show up as a separate trace.

## Go

A function is called in a go routine. A new span is created within this function using `context.Background()`. Since the 
background context is unaware of our trace context, the span belongs to a separate trace.


# 2.2
# Asynchronous

We update our asynchronous calls and pass context to them. Doing so, enables the spans to be created in the parent context.

## Go
Since trace context is stored in a Go `context.Context`. We need to pass this context, and leverage it when creating any 
new span. This may require changes to function and method signatures in order to accept a context object. The best practice
for this in Go, is to pass context as the first parameter.


# 3
# Span Events

Adding events to our spans can be used to understand point in time events in longer running operations, capture details
about errors, and more. Adding Span Events are part of the OpenTelemetry API and can be done to any span that hasn't ended.

## Go
The `span.AddEvent(name, options)` is a variadic function which can receive a set of optional EventOption parameters. 
You can use `trace.WithAttributes(...)` as an EventOption to set attributes on a span event.


# 4
# Span Links
Span Links allow us to connect casually related traces. A span can contain 0 or more links to other spans located in the same or different traces. A popular use case is a batch process which creates multiple jobs, each with their own trace. The traces for each job can be linked to the batch process using span links. Since span Links may be part of sampling decisions, they must be defined at span creation time.

## Go
When creating/starting a span in Go, the variadic function can receive an optional set of `SpanOption` arguments. Using `trace.WithLinks(trace.Link{SpanContext: spanContext})`, links can be added to the span at creation time. Links are created using a `SpanContext` and optional attributes.


# 5.1, 5.2
# Propagation - "Starting Point"

To demonstrate propagation, a new service is added to the stack. This new service, called `name`, contains a list of 
names by year. When called it will make a request to the `year` service to get a year, and return a random name from the
list of names for the given year.

This new service is written only in Go, but can depend on the year service from either Java or Go.

In order to show propagation across different formats, the new service is instrumented using the Honeycomb Beeline for Go
SDK. The Honeycomb Beeline SDKs support the ability to propagate headers in W3C format, which can be understood by 
OpenTelemetry SDKs.


# 5.3, 5.4
# Propagation

Trace propagation allows traces to continue across services, even when different tracing SDKs are used.

In order to propagate traces from Honeycomb Beelines, you need to add tha appropriate tracing propagator to the Beeline's
init, or as part of the outbound call. For the Honeycomb Go Beeline, this is added as part of the outbound call as a 
`propagationHook` function which will look like this to propagate W3C headers: 
```go
func propagateTraceHook(r *http.Request, prop *propagation.PropagationContext) map[string]string {
	ctx := r.Context()
	ctx, headers := propagation.MarshalW3CTraceContext(ctx, prop)
	return headers
}
```

OpenTelemetry specification recommends that trace propagation and parsing is specified at the integration level, and not 
the SDK, though different languages implement this nuance differently.

## Go
As of 0.20.0, the Go Gorilla/mux integration does not specify a propagator. One can be specified with the 
TraceProvider which will be leveraged by all SDKs. The W3C propagator, is specified as a `TextMapPropagator` like this: 
```go
otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))
```


# 6
# Multi-span Attributes

Multi-span Attributes allow you to specify attributes that are automatically applied to all descendant spans, even
across services. Passing multi-span attributes across services, is accomplished with trace propagation using headers. 
Since each attribute requires additional network bandwidth, multi-span attributes should be used with care.

Honeycomb's OpenTelemetry Distribution SDKs, which are wrappers for OpenTelemetry, enable multi-span attributes using 
`Baggage` to propagate the attributes, and a `SpanProcessor` which converts baggage items to attributes on export. 
The Honeycomb OpenTelemetry Distribution SDKs are 100% compatible with all OpenTelemetry APIs.

The `name` service for Java has been added, to demonstrate the multi-span attributes functionality. This service will call the `year` service from either Java or Go. A URL parameter for the service, was added to drive the multi-span attribute. You can control this value by passing a value to the `guess` URL parameter when calling the service.
```http request
http://localhost:6002/name?guess=sophia
```