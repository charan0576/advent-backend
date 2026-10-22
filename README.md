# Advent Tech Studio — Backend (Render Web Service)

FastAPI API + Remotion/Chromium video renderer, packaged as a Docker web service.

## Deploy on Render

1. Push the **contents of this folder** to the root of a GitHub repository. The repository root must contain `Dockerfile`, `render.yaml`, `backend/`, and `renderer/`.
2. In Render, choose **New + → Web Service** and connect the backend repository. Choose **Docker** as the runtime.
3. Set **Root Directory** to `.` when `Dockerfile` is at repository root. Set Dockerfile Path to `./Dockerfile`.
4. Choose a paid instance with enough memory for Remotion/Chromium video rendering. The included `render.yaml` uses a Standard instance and a 10 GB persistent disk mounted at `/data`.
5. Set the environment variables below. If creating from `render.yaml` as a Blueprint, review the same settings and supply the values when asked.
6. Deploy, then verify `https://YOUR-RENDER-SERVICE.onrender.com/health` returns `{"status":"ok"}`.

## Render environment variables

| Name | Value | Required |
|---|---|---|
| `PUBLIC_BASE_URL` | Full Render service URL, e.g. `https://advent-tech-api.onrender.com` (no trailing slash) | Yes, for correct video/QR links |
| `FRONTEND_URL` | Full Vercel production URL, e.g. `https://advent-tech-studio.vercel.app` (no trailing slash). Multiple origins may be comma-separated. | Yes, for QR redirects/CORS |
| `GEMINI_API_KEY` | A valid Gemini API key | Optional; storyline falls back without it |
| `GEMINI_MODEL` | `gemini-3.8-flash` (confirm model access for your key) | Optional; included default |
| `PEXELS_API_KEY` | A valid Pexels API key | Optional; cause artwork fallback is available |
| `CORS_ORIGIN_REGEX` | Optional regex for your own Vercel preview origins only | Optional |

Keep API keys in Render's Environment settings. Never commit `.env` or real keys. `PUBLIC_BASE_URL` and `FRONTEND_URL` are app configuration values, not secrets.

## Persistent storage

The Dockerfile sets `DATA_DIR=/data`. Keep the Render disk mounted at `/data`; profiles, organisation settings, uploads, and MP4 output are stored there. Do not deploy this service on an ephemeral filesystem if those files must survive restarts.

## Local development

From `backend/`, install Python dependencies and run `python -m uvicorn app:app --reload`. Separately run `npm ci` inside `renderer/` if working on the Remotion renderer. The Docker deployment installs both dependency sets.

## Production security warning

This supplied app is a single-workspace demo and **does not implement real user authentication or authorization**. Write routes and video-generation routes can be called by anyone who can reach the API. Do not use it for unrestricted public production use until authentication, authorization, rate limiting, and abuse protection have been implemented. Video jobs are held in memory and can be interrupted by restarts; run a single instance unless job state is moved to durable shared storage/queue.
