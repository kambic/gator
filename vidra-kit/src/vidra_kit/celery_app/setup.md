Here's a **2025-updated, production-grade checklist** of Celery worker best practices that will save you from 95% of real-world headaches (scaling issues, stuck tasks, memory leaks, outages, etc.).

### 1. Worker Architecture & Isolation (Most Important!)
| Practice | Why & How |
|----------|----------|
| One queue per logical workload | Never run everything on the default “celery” queue. Isolate by criticality, latency, or resource needs. |
| Separate workers per queue type | Example: <br>– `-Q critical,high` → low concurrency, fast machines <br>– `-Q default` → general purpose <br>– `-Q low,reports` → high concurrency, maybe cheaper spot instances |
| Use short, meaningful queue names | `send_email`, `video_transcode`, `webhook`, `cleanup` instead of `celery` or random UUIDs |
| Never mix heavy & light tasks on same worker | A 10-minute video transcode will block your 100ms webhook deliveries |

### 2. Worker Command (2025 Gold Standard)
```bash
celery -A proj worker \
  --loglevel=INFO \
  --concurrency=4 \                  # or 0 for eventlet/gevent
  -Q critical,high_priority,default \
  --hostname=worker-%h@%n \          # unique hostname → better monitoring
  --autoscale=10,2 \                 # or use -O fair + pool prefork
  -O fair \                          # prevents head-of-line blocking
  --max-tasks-per-child=200 \        # critical for memory leaks
  --time-limit=3600 --soft-time-limit=3540 \  # kill runaway tasks
  --without-gossip --without-mingle \  # reduces network noise
  -E                                 # send task events → Flower/monitoring
```

### 3. Process Model & Concurrency
| Pool | When to use | Recommended concurrency |
|------|-------------|-------------------------|
| **prefork** (default) | CPU-bound tasks (data crunching, ML inference) | `2–4 × CPU cores` |
| **eventlet/gevent** | IO-bound (thousands of HTTP calls, websockets) | 500–10,000 (start with 1000) |
| **threads** | Rarely – only if you have thread-safe code | 2–8 |
| **solo** | Debugging or single-task workers | 1 |

Use `eventlet` example:
```bash
pip install eventlet
celery -A proj worker -P eventlet -c 1000 -Q webhooks,notifications
```

### 4. Memory & Stability
| Setting | Value | Reason |
|---------|-------|--------|
| `--max-tasks-per-child` | 100–500 | Reload worker after N tasks → fight memory leaks (especially Pillow, pandas, etc.) |
| `--max-memory-per-child` | 500MB–2GB | New in Celery 5.3+ – kills workers that grow too big |
| Warm shutdown | `celery multi ... --pidfile` + SIGTERM | Give tasks time to finish |

### 5. Task Design Best Practices
- Always use **time limits** (`time_limit` / `soft_time_limit`)
- Never use `ignore_result=True` blindly → results backend can explode
- Use `acks_late=True` + `task_reject_on_worker_lost=True` for critical tasks
- Idempotency everywhere (retrying a task twice must be safe)
- Prefer `chunk()` / `group()` over sending 100k tasks at once

### 6. Monitoring & Observability (2025 stack)
| Tool | Must-have |
|------|-----------|
| Flower (or Celery 5.4 built-in dashboard) | Real-time view |
| Prometheus + celery-exporter | Metrics (queue length, task rates) |
| Sentry / Rollbar | Task exceptions |
| Grafana dashboards | Queue lengths, worker count, latency |

Key metrics to alert on:
- Queue length > threshold
- Worker count drops
- Task runtime > 99th percentile
- Failed tasks rate

### 7. Queue & Broker Specific Tips
| Broker | Best practice |
|--------|---------------|
| **RabbitMQ** | Use quorum queues for important queues (`x-queue-type: quorum`) <br> Enable priority with `x-max-priority: 10` |
| **Redis** | Use separate Redis DB or instance for Celery <br> Enable `task_acks_late` + Redis Streams (Celery 5.4+) for better reliability |
| **SQS** | One queue per task type (SQS doesn’t support dynamic queues well) <br> Use visibility timeout > task time limit |

### 8. Deployment (Kubernetes vs Classic)
| Environment | Recommended pattern |
|-------------|---------------------|
| Kubernetes | One pod per worker type (critical, default, cpu-heavy) <br> Use HorizontalPodAutoscaler on queue length metrics |
| Docker/EC2 | systemd or supervisor with multiple worker processes <br> Use `--autoscale` or custom autoscaler watching queue length |

### TL;DR – Minimal Production Command Set (2025)
```bash
# Critical tasks (low latency)
celery -A proj worker -Q critical -c 4 --time-limit=60 -O fair --max-tasks-per-child=200 --hostname=critical@%h

# CPU-heavy tasks
celery -A proj worker -Q heavy -c 8 --time-limit=7200 --max-tasks-per-child=100 --hostname=heavy@%h

# IO-heavy (webhooks, APIs)
celery -A proj worker -P eventlet -c 1000 -Q notifications,webhooks --hostname=io@%h
```

Follow these and your Celery setup will scale to millions of tasks/day without mysterious crashes or stuck queues.

Need a ready-to-copy systemd/K8s config for your exact stack? Just tell me your broker + deployment method.
