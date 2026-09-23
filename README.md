# SmartScreening

## Development setup

Use the project virtual environment so Django and project dependencies are
available in the same interpreter:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

The default development database is SQLite. The default organization is
available at `/account/org/pouyamed/` after migrations are applied.

## Multilingual routes

Shared application routes use Django internationalization and are available
under language prefixes:

```text
/fa/   Persian (default)
/en/   English
/ar/   Arabic
```

Use the language menu in the shared header to switch languages. Authenticated
users also have their preference saved on `Profile.language`; organizations can
set their default language in the Django admin. Older suffixed URLs remain as
compatibility aliases while existing bookmarks are migrated.

When adding interface text, use Django translation tags or lazy translations:

```django
{% load i18n %}
{% translate "Start screening" %}
```

Update catalogs with `makemessages` and compile them before deployment:

```bash
.venv/bin/python manage.py makemessages -l fa -l ar
.venv/bin/python manage.py compilemessages
```

Persist screening answers in language-neutral values such as `Yes` and `No`;
translate those values only when rendering a page or PDF report.

## Verification

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python -m pip check
```

## Production configuration

Use the production settings module and provide the required environment
variables before starting the WSGI server:

```bash
export DJANGO_SETTINGS_MODULE=smartscreening.settings_production
export DJANGO_SECRET_KEY='replace-with-a-long-random-secret'
export DJANGO_ALLOWED_HOSTS='screening.example.com'
export DJANGO_DB_ENGINE=postgresql
export DJANGO_DB_NAME=smartscreening
export DJANGO_DB_USER=smartscreening
export DJANGO_DB_PASSWORD='replace-with-the-database-password'
export DJANGO_DB_HOST=127.0.0.1

.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/gunicorn smartscreening.wsgi:application
```

Screening records are organization-scoped. Organization administrators can
manage active members and view reports only for their organization.

## Follow-up programs and SMS

Follow-up programs are configured in Django admin under **Screening follow-up**:

1. Create one `Follow-up program` for a disease/assessment.
2. Select the result statuses that should activate it, or leave them empty to
   match every result.
3. Enable PDF SMS if the report link should be sent immediately (or after a
   delay), then add ordered follow-up steps with their reminder delays and
   localized SMS text.
4. Users can see their active plans at the **Follow-up** page. Their mobile
   number can be entered at registration or maintained in the Profile admin.

SMS delivery is disabled until these environment variables are configured:

```bash
export KAVENEGAR_API_KEY='your-api-key'
export KAVENEGAR_SENDER='your-sender-number'
export SMARTSCREENING_PUBLIC_URL='https://screening.example.com'
```

`SMARTSCREENING_PUBLIC_URL` must be reachable by the user; do not use
`localhost` for production SMS links. Run the delivery worker periodically
with cron, systemd, or a task queue:

```bash
.venv/bin/python manage.py process_followups
```

Use `--dry-run` to inspect due reminders and `--retry-failed` to retry failed
deliveries. The provider adapter uses Kavenegar’s REST `sms/send.json` endpoint
and records the provider message ID and status for auditability.

## Docker deployment on a VPS

The production stack contains Django/Gunicorn, PostgreSQL, Caddy HTTPS,
persistent media/static volumes, and a follow-up SMS scheduler.

1. Install Docker Engine and the Docker Compose plugin on the VPS.
2. Copy the project to the server and create the private environment file:

```bash
cp .env.example .env
nano .env
```

Set a strong `DJANGO_SECRET_KEY`, database password, real `APP_DOMAIN`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and
`SMARTSCREENING_PUBLIC_URL`. Point the domain DNS A/AAAA record to the VPS.
Caddy will request and renew HTTPS certificates automatically.

Start the stack:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

Create the first administrator:

```bash
docker compose exec web python manage.py createsuperuser
```

The application is then available at `https://APP_DOMAIN/`. PostgreSQL data,
media uploads, collected static files, and Caddy certificates are stored in
Docker volumes. Back up at least `postgres_data` and `media_data` regularly.

For a configuration-only validation using the example values:

```bash
ENV_FILE=.env.example docker compose --env-file .env.example config --quiet
```

## GitHub publication

The repository excludes local virtual environments, `.env` files, SQLite
databases, uploaded media, and generated static output. Source assets belong
 in `assets/`; `collectstatic` recreates the deployable static directory.

Before publishing, review the staged file list and run the checks:

```bash
git diff --cached --name-status
git diff --cached --check
.venv/bin/python manage.py check
.venv/bin/python manage.py test
.venv/bin/python manage.py makemigrations --check --dry-run
```

Then create and push a commit:

```bash
git commit -m "Prepare SmartScreening for deployment"
git push smartscreening main
```

Never commit `.env`, database files, uploaded organization logos, or SMS/API
credentials. Use `.env.example` as the public configuration template.
