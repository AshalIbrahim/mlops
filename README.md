
What is Prometheus? (The Data Collector)

Think of Prometheus as a data journalist. Its only job is to collect important numbers (metrics) from our applications and store them with a timestamp.

How it Works: Prometheus reads a configuration file (monitoring/prometheus.yml) that gives it a list of "targets" to check. Every 15 seconds, it visits a special webpage on each target (like http://localhost:8000/metrics) and "scrapes" all the metrics it finds there.

What it Collects: It stores this information in its own time-series database. For our project, it collects data like:

How many HTTP requests our API receives.

How long our ML model takes to make a prediction.

Whether our data processing script succeeded or failed.

The CPU and Memory usage of the server.

In Short: Prometheus is the backend engine that collects and stores all the raw monitoring data.

What is Grafana? (The Data Visualizer)

Think of Grafana as the graphic designer who turns the raw data collected by Prometheus into beautiful, easy-to-understand dashboards.

How it Works: Grafana does NOT store any data itself. Instead, you tell it how to connect to a "data source," which in our case is Prometheus.

What it Does: You build dashboards in Grafana by creating panels. Each panel is a chart, graph, or single number. For each panel, you write a query to ask Prometheus for specific data. Grafana then visualizes the answer.

In Short: Grafana is the frontend that we look at. It asks Prometheus for data and displays it visually on dashboards.

How They Work Together: A Simple Workflow

Our Python application (app.py) runs and exposes its current metrics (like http_requests_total) on a /metrics webpage.

Prometheus visits this webpage every 15 seconds, saves the values, and stores them in its database.

We open Grafana in our browser and look at a dashboard.

A panel on the dashboard asks Prometheus, "Hey, what was the rate of HTTP requests over the last 5 minutes?"

Prometheus answers with the data, and Grafana draws a graph showing the request rate over time.
