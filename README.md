# 🛠️ djresttoolkit (django rest toolkit)

[![PyPI version](https://img.shields.io/pypi/v/djresttoolkit.svg)](https://pypi.org/project/djresttoolkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/djresttoolkit.svg)](https://pypi.org/project/djresttoolkit/)
[![License](https://img.shields.io/pypi/l/djresttoolkit.svg)](https://github.com/shaileshpandit141/djresttoolkit/blob/main/LICENSE)

djresttoolkit is a collection of utilities and helpers for Django and Django REST Framework (DRF) that simplify common development tasks such as API handling, authentication, and email sending and much more.

## ✨ Features

- Django REST Framework helpers (serializers, views, pagination, etc.)
- Django utilities (e.g., email sending, model mixins)
- Ready-to-use shortcuts to speed up API development
- Lightweight, no unnecessary dependencies
- Type Safe - written with modern Python type hints.

## 📦 Installation

- **By using uv:**
  
    ```bash
    uv add djresttoolkit
    ````

- **By using pip:**

    ```bash
    pip install djresttoolkit
    ````

## 📚 All API Reference

### 1. DB Seed Utilities

#### `Generator`

```python
from djresttoolkit.dbseed.models import Generator, Gen, Field
```

- `Gen`: Pre-initialized **Faker** instance for generating fake data.
- `Field`: Alias for `pydantic.Field` to define seed model fields.

#### Example

```python
from djresttoolkit.dbseed.models import SeedModel
from myapp.models import User

class UserSeedModel(SeedModel):
    __model__ = User

    username: str = Field(default_factory=lambda: Gen.user_name())
    email: str = Field(default_factory=lambda: Gen.email())
```

#### `manage.py` Command: `dbseed`

Seed the database from all `dbseed` directories in installed apps.

```bash
python manage.py dbseed [--count 5] [--model User] [--seed 42]
```

#### Options

- `--count`: Number of records per model (default: 5).
- `--model`: Specific model name to seed (optional).
- `--seed`: Faker seed for reproducible data (optional).

#### Behavior

- Auto-discovers all `dbseed` models in installed apps.
- Handles ForeignKey, OneToOneField, and ManyToMany relationships.
- Uses transactions to ensure safe creation of records.
- Logs errors for failed instance creation but continues seeding.

#### Command Example

```bash
# Seed 10 records for all models
python manage.py dbseed --count 10

# Seed only the User model with fixed Faker seed
python manage.py dbseed --model User --seed 42
```

Here’s a **concise API reference** for your database flush management command for `djresttoolkit`:

---

### 2. DB Flush Command

```python
from djresttoolkit.management.commands import flush
```

#### `manage.py dbflush`

Command to **delete all records** from the database for all models or a specific model and **reset auto-increment IDs**.

#### Usage

```bash
python manage.py flush [--model ModelName] [--yes]
```

#### dbflush command options

- `--model`: Name of the model to flush (case-sensitive, e.g., `User`). If omitted, flushes all models.
- `--yes`: Skip confirmation prompt. Without this, the command asks for confirmation before deleting.

#### dbflush command behavior

- Deletes all records for the specified model or all models.
- Resets primary key sequences for supported databases:

  - PostgreSQL: `ALTER SEQUENCE ... RESTART WITH 1`
  - SQLite: Deletes from `sqlite_sequence` table
  - Others: Logs a warning (not implemented).
- Uses transactions to ensure safe operations.

#### dbflush command example

```bash
# Flush all models with confirmation
python manage.py dbflush

# Flush a specific model (User) with confirmation
python manage.py dbflush --model User

# Flush all models without prompt
python manage.py dbflush --yes
```

#### Output

```bash
Flushed 10 records from model "User" and reset IDs.
```

or

```bash
Flushed 120 records from all models and reset IDs.
```

### 3. EnvBaseSettings

```python
from djresttoolkit.envconfig import EnvBaseSettings
```

#### `EnvBaseSettings`

A **base settings class** for managing application configuration using:

- YAML files (default `.environ.yaml`)
- Environment variables (default `.env`)

Supports **nested configuration** using double underscores (`__`) in environment variable names.

#### Class Attributes

| Attribute      | Type                 | Default         | Description                                                        |
| -------------- | -------------------- | --------------- | ------------------------------------------------------------------ |
| `env_file`     | `str`                | `.env`          | Environment variable file path.                                    |
| `yaml_file`    | `str`                | `.environ.yaml` | YAML configuration file path.                                      |
| `model_config` | `SettingsConfigDict` | —               | Pydantic settings configuration (file encoding, nested delimiter). |

#### Methods

#### `load(cls, *, env_file: str | None = None, ymal_file: str | None = None, warning: bool = True) -> EnvBaseSettings`

Loads configuration from **YAML first**, then overrides with **environment variables**.

#### Parameters

- `env_file` — Optional custom `.env` file path.
- `ymal_file` — Optional custom YAML file path.
- `warning` — Emit a warning if YAML file is missing (default `True`).

#### Returns

- Instance of `EnvBaseSettings` (or subclass) with loaded configuration.

#### Raises

- `UserWarning` if YAML file not found and `warning=True`.

### Usage Example

```python
from djresttoolkit.envconfig import EnvBaseSettings

class EnvSettings(EnvBaseSettings):
    debug: bool = False
    database_url: str

# Load settings
settings = EnvSettings.load(warning=False)

print(settings.debug)
print(settings.database_url)
```

#### Features

- Prioritizes `.env` variables over YAML.
- Supports nested keys: `DATABASE__HOST` → `settings.database.host`.
- Designed to be subclassed for project-specific settings.

### 4. EmailSender

```python
from djresttoolkit.mail import EmailSender, EmailContent, EmailTemplate
```

### `EmailSender`

Send templated emails.

#### Init

```python
EmailSender(email_content: EmailContent | EmailContentDict)
```

#### EmailSender Methods

```python
send(to: list[str], exceptions: bool = False) -> bool
```

- `to`: recipient emails
- `exceptions`: raise on error if `True`, else logs error
- Returns `True` if sent, `False` on failure

#### Example for sending an email

```python
content = EmailContent(
    subject="Hello",
    from_email="noreply@example.com",
    context={"username": "Alice"},
    template=EmailTemplate(
        text="emails/welcome.txt",
        html="emails/welcome.html"
    )
)
EmailSender(content).send(to=["user@example.com"])
```

#### `EmailContent`

- `subject`, `from_email`, `context`, `template` (EmailTemplate)

#### `EmailTemplate`

- `text`, `html` — template file paths

### 5. Custom DRF Exception Handler

```python
from djresttoolkit.views import exception_handler
```

### `exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None`

A DRF exception handler that:

- Preserves DRF’s default exception behavior.
- Adds throttling support (defaults to `AnonRateThrottle`).
- Returns **429 Too Many Requests** with `retry_after` if throttle limit is exceeded.

#### Exception Handler Parameters

- `exc`: Exception object.
- `context`: DRF context dictionary containing `"request"` and `"view"`.

#### Returns Type of Exception Handler

- `Response` — DRF Response object (with throttling info if applicable), or `None`.

#### Settings Configuration

In `settings.py`:

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'djresttoolkit.views.exception_handler',
    # Other DRF settings...
}
```

#### Throttle Behavior

- Uses `view.throttle_classes` if defined, else defaults to `AnonRateThrottle`.
- Tracks requests in cache and calculates `retry_after`.
- Cleans expired timestamps automatically.

### 6. Response Time Middleware

```python
from djresttoolkit.middlewares import ResponseTimeMiddleware
```

### `ResponseTimeMiddleware`

Middleware to calculate and log **HTTP response time** for each request.

#### Constructor from ResponseTimeMiddleware

```python
ResponseTimeMiddleware(get_response: Callable[[HttpRequest], HttpResponse])
```

- `get_response`: The next middleware or view callable.

#### Response Time Middleware Usage

Add it to your Django `MIDDLEWARE` in `settings.py`:

```python
MIDDLEWARE = [
    # Other middlewares...
    'djresttoolkit.middlewares.ResponseTimeMiddleware',
]
```

#### Response Time Middleware Behavior

- Measures the time taken to process each request.
- Adds a header `X-Response-Time` to each HTTP response.
- Logs the response time using Django's logging system.

#### The response headers will include

```json
X-Response-Time: 0.01234 seconds
```

#### Logs a message

```bash
INFO: Request processed in 0.01234 seconds
```

### 7. Throttle Utilities

#### `ThrottleInfoJSONRenderer`

```python
from djresttoolkit.renderers import ThrottleInfoJSONRenderer
```

A custom DRF JSON renderer that **automatically attaches throttle information to response headers**.

#### Usage (settings.py)

```python
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "djresttoolkit.renderers.ThrottleInfoJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}
```

When enabled, every response includes throttle headers like:

```plaintext
X-Throttle-User-Limit: 100
X-Throttle-User-Remaining: 98
X-Throttle-User-Reset: 2025-08-18T07:30:00Z
X-Throttle-User-Retry-After: 0
```

#### `ThrottleInspector`

```python
from djresttoolkit.throttling import ThrottleInspector
```

Utility class to **inspect DRF throttle usage** for a view or request.

#### Constructor for ThrottleInspector

```python
ThrottleInspector(
    view: APIView,
    request: Request | None = None,
    throttle_classes: list[type[BaseThrottle]] | None = None,
)
```

#### Key Methods

- `get_details() -> dict[str, Any]`
  Returns structured throttle info: limit, remaining, reset time, retry\_after.

- `attach_headers(response: Response, throttle_info: dict | None)`
  Attaches throttle data to HTTP headers.

## 🛠️ Planned Features

- Add more utils

## 🤝 Contributing

Contributions are welcome! Please open an issue or PR for any improvements.

## 📜 License

MIT License — See [LICENSE](LICENSE).

## 👤 Author

For questions or assistance, contact **Shailesh** at [shaileshpandit141@gmail.com](mailto:shaileshpandit141@gmail.com).
