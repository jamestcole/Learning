# Prometheus Queries for Flask App Monitoring
## Set up your Flask App and Prometheus containers

- check that wss agent is not causing issues , the code should work as stated
```
docker-compose up --build
```
## 📌 Basic Queries to Get Started

### 1️⃣ Check all available metrics:
```promql
{__name__=~".*"}
```
This returns all metrics being scraped, including the ones from your Flask app.

### 2️⃣ View total requests received by your Flask app:
```promql
flask_app_requests_total
```
This shows the total count of requests tracked by the `REQUEST_COUNT` counter.

### 3️⃣ Check requests received per second (rate over the last minute):
```promql
rate(flask_app_requests_total[1m])
```
This calculates the per-second request rate over the last **1 minute**.

### 4️⃣ Check requests received per second (rate over 5 minutes):
```promql
rate(flask_app_requests_total[5m])
```
This smooths out fluctuations by calculating the rate over **5 minutes**.

### 5️⃣ Find the highest request rate in the last 10 minutes:
```promql
max(rate(flask_app_requests_total[10m]))
```
This helps you identify traffic spikes.

---

## 🚀 How to Run These Queries

1. **Open Prometheus UI** at:  
   👉 [http://localhost:9090](http://localhost:9090)
2. Go to the **"Graph"** tab.
3. Enter any of the queries above and hit **"Execute"**.
4. Switch between **Graph** and **Table** views to analyze results.

---

## 🔄 Next Steps
- Try making some requests to your Flask app:
  ```bash
  curl http://localhost:5000/
  ```
- Then **re-run the queries** in Prometheus to see how the metrics change!

