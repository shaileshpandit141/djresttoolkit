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

## 📚 API Reference

### 1. EmailSender

```python
from djresttoolkit.mail import EmailSender, EmailContent, EmailTemplate
```

### `EmailSender`

Send templated emails.

#### Init

```python
EmailSender(email_content: EmailContent | EmailContentDict)
```

#### Methods

```python
send(to: list[str], exceptions: bool = False) -> bool
```

- `to`: recipient emails
- `exceptions`: raise on error if `True`, else logs error
- Returns `True` if sent, `False` on failure

#### Example

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

### 2. Custom DRF Exception Handler

```python
from djresttoolkit.views import exception_handler
```

### `exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None`

A DRF exception handler that:

- Preserves DRF’s default exception behavior.
- Adds throttling support (defaults to `AnonRateThrottle`).
- Returns **429 Too Many Requests** with `retry_after` if throttle limit is exceeded.

#### Parameters

- `exc`: Exception object.
- `context`: DRF context dictionary containing `"request"` and `"view"`.

#### Returns

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

### 3. Response Time Middleware

```python
from djresttoolkit.middlewares import ResponseTimeMiddleware
```

### `ResponseTimeMiddleware`

Middleware to calculate and log **HTTP response time** for each request.

#### Constructor

```python
ResponseTimeMiddleware(get_response: Callable[[HttpRequest], HttpResponse])
```

- `get_response`: The next middleware or view callable.

#### Usage

Add it to your Django `MIDDLEWARE` in `settings.py`:

```python
MIDDLEWARE = [
    # Other middlewares...
    'djresttoolkit.middlewares.ResponseTimeMiddleware',
]
```

#### Behavior

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

## 🛠️ Planned Features

- Add more utils

## 🤝 Contributing

Contributions are welcome! Please open an issue or PR for any improvements.

## 📜 License

MIT License — See [LICENSE](LICENSE).

## 👤 Author

For questions or assistance, contact **Shailesh** at [shaileshpandit141@gmail.com](mailto:shaileshpandit141@gmail.com).
