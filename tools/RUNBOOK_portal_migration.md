# portal.astrastaging.com — deploy + fallback runbook

**Status: LIVE on DigitalOcean as of 2026-04-24.**

## Architecture

```
  Toky webhook / browser / mobile API client
        │
        ▼
  DNS  portal.astrastaging.com  →  137.184.42.40   (DO droplet)
        │
        ▼
  Apache  :443 (TLS via certbot, auto-renew)       /etc/apache2/sites-available/portal-astrastaging-le-ssl.conf
    ├── /static/*        →  direct file serve from /var/www/as_website/static
    └── everything else  →  127.0.0.1:5003
        │
        ▼
  portal.service (systemd)                         /etc/systemd/system/portal.service
     /var/www/as_website/.venv/bin/python -m as_webapp.main
     env: AS_WEBAPP_PORT=5003, AS_WEBAPP_RELOAD=false, + .env
     logs: /var/log/as_webapp.log
```

## Critical files on DO

| Path | Purpose |
|---|---|
| `/var/www/as_website/` | code + git checkout |
| `/var/www/as_website/.env` | secrets (chmod 600, NOT in git) |
| `/var/www/as_website/data/zoho_sync.db` | Zoho snapshot + Toky tables (authoritative) |
| `/var/www/as_website/data/email.db` | kenneth@ IMAP scrape |
| `/var/www/as_website/data/toky_audio/` | raw Toky mp3s |
| `/var/www/as_website/data/staging_media/` | consultation photos/videos |
| `/etc/systemd/system/portal.service` | unit file |
| `/etc/apache2/sites-available/portal-astrastaging-le-ssl.conf` | reverse proxy + TLS |
| `/var/log/as_webapp.log` | app stdout/stderr |

## Day-to-day ops

### Deploy a code change
```bash
# on m4
git commit -am "..." && git push

# on DO
ssh root@citygatesuites.com "cd /var/www/as_website && git pull && systemctl restart portal.service"
```

### Tail live logs
```bash
ssh root@citygatesuites.com "tail -f /var/log/as_webapp.log"
```

### Restart the portal
```bash
ssh root@citygatesuites.com "systemctl restart portal.service"
```

### Rotate an API key (.env)
```bash
ssh root@citygatesuites.com
vim /var/www/as_website/.env
systemctl restart portal.service
```

## Fallback — if portal.astrastaging.com goes down

Scenarios where you need this:
- DO droplet unreachable / hardware failure
- Apache config disaster
- Runaway Python process wedges uvicorn

### Option 1 — systemd restart (first try)
```bash
ssh root@citygatesuites.com "systemctl restart portal.service; systemctl status portal.service"
```
Resolves >90% of live-service issues.

### Option 2 — revert the last code push
```bash
ssh root@citygatesuites.com "cd /var/www/as_website && git log --oneline -5"
# Find the last-known-good commit hash
ssh root@citygatesuites.com "cd /var/www/as_website && git reset --hard <hash> && systemctl restart portal.service"
```

### Option 3 — flip DNS back to m4 Tailscale Funnel (cold standby)
Use this if DO is completely down and you need the portal back in minutes.

1. **Bring up m4 portal** (currently stopped):
   ```bash
   # on m4
   cd /Users/kennethjin/Desktop/development/as_website
   nohup .venv/bin/python -m as_webapp.main > /tmp/as_webapp.log 2>&1 &
   ```

2. **Re-enable Tailscale Funnel** for the webhook path:
   ```bash
   /Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --bg --set-path=/api/v1/toky/webhook http://localhost:5002/api/v1/toky/webhook
   # public URL: https://m4.taile1438a.ts.net/api/v1/toky/webhook
   ```

3. **Flip DNS** — change `portal.astrastaging.com` A record from DO IP to a CNAME pointing at the Tailscale hostname:
   ```bash
   export DIGITALOCEAN_ACCESS_TOKEN=$(security find-generic-password -s digitalocean_api_token -w)
   # Delete current A record
   doctl compute domain records list astrastaging.com --format ID,Type,Name,Data | grep "A.*portal"
   # Use the ID from above
   doctl compute domain records delete astrastaging.com <id> --force
   # Add CNAME to Tailscale
   doctl compute domain records create astrastaging.com \
     --record-type CNAME \
     --record-name portal \
     --record-data m4.taile1438a.ts.net. \
     --record-ttl 60
   ```

4. **Re-point Toky webhook** (can't rely on DO's vhost):
   ```bash
   cd /Users/kennethjin/Desktop/development/as_website
   # Delete current (DO-pointed) webhook ids
   .venv/bin/python tools/register_toky_webhook.py list
   .venv/bin/python tools/register_toky_webhook.py delete 1612
   .venv/bin/python tools/register_toky_webhook.py delete 1613
   # Register new ones pointed at m4 Tailscale
   .venv/bin/python tools/register_toky_webhook.py register https://m4.taile1438a.ts.net/api/v1/toky/webhook
   ```

5. **Sanity test**:
   ```bash
   curl -I https://portal.astrastaging.com/api/v1/hello
   # (routes through Tailscale Funnel to m4 now)
   ```

6. **Roll back to DO once it's fixed** — reverse steps 3–4.

### Known shortcomings of the Option 3 fallback
- m4 DB is **stale** (dev copy, last seeded 2026-04-24). Any writes during the DO outage happen on m4's dev DB. When DO comes back, reconcile manually.
- Tailscale Funnel path-scoping only covers `/api/v1/toky/webhook`. The `/signin`, `/calls`, `/analytics` pages need a broader Funnel scope — run
  ```
  tailscale funnel --bg http://localhost:5002
  ```
  to expose all paths, at the cost of no path gating.
- Google OAuth won't accept `m4.taile1438a.ts.net` as a JS origin unless you add it. For a true full-service fallback, add that host to the OAuth client too (pre-authorize in advance so no rush work during an outage).

## DNS + certs

- Portal DNS: `portal.astrastaging.com A 137.184.42.40` (TTL 60, managed in DO DNS)
- TLS: Let's Encrypt via certbot, expires 2026-07-23, auto-renews
- Renew manually if needed: `ssh root@citygatesuites.com "certbot renew"`

## Backup strategy

- DB snapshots: nightly `rsync data/*.db root@citygatesuites.com:/var/www/backups/daily/` (cron TBD)
- Archive: `/var/www/backups/` on DO + mirror to m4 under `data/do_archives/`
- Code: git at github.com/fskenneth/as_website, m4 is a second clone

## Toky webhooks (current)

```
id=1612  event=inbound_call_ended    url=https://portal.astrastaging.com/api/v1/toky/webhook
id=1613  event=outbound_call_ended   url=https://portal.astrastaging.com/api/v1/toky/webhook
```
Manage with `.venv/bin/python tools/register_toky_webhook.py {list,register,delete}`.
