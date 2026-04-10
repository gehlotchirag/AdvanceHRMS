# Deploy AdvanceHR on [Railway](https://railway.app/)

## 1. Create the project

1. Open Railway → **New Project** → **Deploy from GitHub repo** → select `gehlotchirag/AdvanceHRMS` (or your fork).
2. Add **PostgreSQL**: **New** → **Database** → **PostgreSQL**. Railway injects `DATABASE_URL` automatically when the database is attached to the same service (or use **Variables** → **Add reference** to the Postgres plugin’s `DATABASE_URL`).

## 2. Required variables

Set these on the **web service** (mark **Available at Build Time** where noted):

| Variable | Example | Build-time |
|----------|---------|------------|
| `SECRET_KEY` | Long random string ([djecrety](https://djecrety.ir/) or `python -c "import secrets; print(secrets.token_urlsafe(50))"`) | Yes |
| `DEBUG` | `False` | Yes |
| `ALLOWED_HOSTS` | `*` (tighten later) or comma-separated hosts | Yes |
| `CSRF_TRUSTED_ORIGINS` | `https://YOUR-SERVICE.up.railway.app` (optional if `RAILWAY_PUBLIC_DOMAIN` is set) | Yes |
| `DATABASE_URL` | *(Reference from Postgres)* | Yes |
| `DB_INIT_PASSWORD` | Random long string (used during DB init flows) | No |

Optional: `TIME_ZONE` (default `Asia/Kolkata` in `.env.dist`).

Railway sets `PORT` and usually `RAILWAY_PUBLIC_DOMAIN` when you assign a public URL. The app adds that domain to `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` automatically when `RAILWAY_PUBLIC_DOMAIN` is present.

## 3. Attach Postgres to the app

- In the **web service** → **Variables** → **Add variable** → **Database** → select Postgres → add **`DATABASE_URL`** (reference).

## 4. Generate a public URL

**Settings** → **Networking** → **Generate domain**. Open the URL; migrations run on deploy via `preDeployCommand` in `railway.toml`.

## 5. Docker image on Railway (Dockerfile)

`docker/entrypoint.sh` runs **migrate** (unless skipped) and **collectstatic** before Gunicorn. Long **migrate** runs delay binding to `PORT`, so health checks can show **service unavailable** (503).

**Recommended:**

1. In the **web** service → **Variables**, set **`SKIP_STARTUP_MIGRATE`** = **`1`**.
2. In the same service → **Settings** → **Deploy** → find **Pre-deploy command** (or **Add pre-deploy step**) and set:

   ```bash
   python manage.py migrate --noinput
   ```

   Railway runs this **after the image is built** and **before** the new deployment is considered healthy. It uses your service env vars (including `DATABASE_URL`). Use **migrate only** here — not `collectstatic`, because [pre-deploy runs in a separate container whose filesystem is not kept](https://docs.railway.app/deployments/pre-deploy-command); **collectstatic** still runs in `entrypoint.sh` on each web container start.

3. Redeploy.

## 6. Media / uploads

The container filesystem is **ephemeral**. For production file uploads, configure cloud storage (see `.env.dist` GCP section) or Railway **Volumes** and point `MEDIA_ROOT` accordingly.

## 7. First login

Complete the in-app database initialization wizard if prompted, or create a superuser from Railway **Shell**:

```bash
python manage.py createsuperuser
```
