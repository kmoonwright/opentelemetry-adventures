# Honeycomb Advanced Instrumentation Workshop

Exercises to help you learn advanced instrumentation techniques with OpenTelemetry and Honeycomb. 
To get the most value from these examples you are expected to have a basic knowledge of distributed tracing.

## Workshop slides

This workshop is meant to be an instructor led workshop, but that shouldn't prevent anyone from doing the workshop themselves. 
Follow along with the [slides](https://docs.google.com/presentation/d/1pYNzZSUFqzF124SkqvXCUZ4JFHs0v_uyQtqyyr9BZYA/edit?usp=sharing).
Make sure to read the speaker notes to get full context on the slide content.


# 1.1
# Manual Instrumentation - "Starting point"

This is the starting point for all the examples. It consists of a service that will return a random year between 
2015 and 2020. The service is duplicated in Java and Go for this workshop.

When launched either service will listen on port `6001` for the `/year` endpoint.

# 1.2
# Manual Instrumentation

Manual instrumentation is adding attributes to existing spans, and creating new spans (or traces) to better understand 
our code.


# 2.1
# Asynchronous - "Starting Point"
This marks the starting point to instrument and understand asynchronous operations in a service. Here services have a new
asynchronous operation added. That operation is also instrumented, but the spans show up as a separate trace.

# 2.2
# Asynchronous
We update our asynchronous calls and pass context to them. Doing so, enables the spans to be created in the parent context.


# 3.1
# Span Events
Adding events to our spans can be used to understand point in time events in longer running operations, capture details
about errors, and more. Adding Span Events are part of the OpenTelemetry API and can be done to any span that hasn't ended.


# 4
# Span Links
Span Links allow us to connect casually related traces. A span can contain 0 or more links to other spans located in the 
same or different traces. A popular use case is a batch process which creates multiple jobs, each with their own trace. 
The traces for each job can be linked to the batch process using span links. Since span Links may be part of sampling 
decisions, they must be defined at span creation time.


# 5
# Propagation - "Starting Point"

To demonstrate propagation, a new service is added to the stack. This new service, called `name`, contains a list of 
names by year. When called it will make a request to the `year` service to get a year, and return a random name from the
list of names for the given year.

This new service is written only in Go, but can depend on the year service from either Java or Go.

In order to show propagation across different formats, the new service is instrumented using the Honeycomb Beeline for Go
SDK. The Honeycomb Beeline SDKs support the ability to propagate headers in W3C format, which can be understood by 
OpenTelemetry SDKs.
