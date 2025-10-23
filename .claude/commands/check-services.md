---
description: Check health status of all services (Rails, Python, PostgreSQL)
---

Please check the health status of all Mosaic services:

1. Check if PostgreSQL is running (pg_isready)
2. Check if Rails server is accessible (curl localhost:3000)
3. Check if Python AI service is accessible (curl localhost:8000/api/v1/agents/status)
4. Report the status of each service

Use the Bash tool to execute these health checks and provide a status report.
