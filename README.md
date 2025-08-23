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

### 1. DB Seed Utilities — API Reference

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

### 2. DB Flush Command — API Reference

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

### 3. EnvBaseSettings — API Reference

```python
from djresttoolkit.envconfig import EnvBaseSettings
```

#### `EnvBaseSettings`

A **base settings class** for managing application configuration using:

- YAML files (default `.environ.yaml`)
- Environment variables (default `.env`)

Supports **nested configuration** using double underscores (`__`) in environment variable names.

#### Class Attributes

- Attributes
  - `env_file`
    - Type: `str`
    - Default: `.env`
    - Description: Environment variable file path.
  - `yaml_file`
    - Type: `str`
    - Default: `.environ.yaml`
    - Description: YAML configuration file path.
  - `model_config`
    - Type: `SettingsConfigDict`
    - Description: Pydantic settings configuration (file encoding, nested delimiter).

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

class EnvSettings(EnvBaseSettings["EnvSettings"]):
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

### 4. EmailSender — API Reference

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

### 5. Custom DRF Exception Handler — API Reference

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

### 6. Response Time Middleware — API Reference

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

### 7. Throttle Utilities — API Reference

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

### 8. AbsoluteUrlFileMixin — API Reference

```python
from djresttoolkit.serializers.mixins import AbsoluteUrlFileMixin
```

### `AbsoluteUrlFileMixin`

A **serializer mixin** that converts **FileField** and **ImageField** URLs to **absolute URLs**, ensuring compatibility with cloud storage backends.

---

### Attributes

- `file_fields`
- type: `list[str] | None`
- default: `None`
- description: Manual list of file field names for non-model serializers.

### Absolute Url File Mixin Methods

#### `to_representation(self, instance: Any) -> dict[str, Any]`

- Overrides default serializer `to_representation`.
- Enhances all file-related fields in the serialized output to **absolute URLs**.

#### `enhance_file_fields(self, instance: Any, representation: dict[str, Any], request: Any) -> dict[str, Any]`

- Core logic to process each file field.
- Converts relative URLs to absolute URLs using `request.build_absolute_uri()`.
- Supports model serializers or manual `file_fields`.
- Logs warnings if request context is missing or file is not found.

#### Exceptions

- `MissingRequestContext`: Raised if the request object is missing in serializer context and `DEBUG=True`.

### Absolute Url File Mixin Example

```python
from rest_framework import serializers
from djresttoolkit.serializers.mixins import AbsoluteUrlFileMixin
from myapp.models import Document

class DocumentSerializer(AbsoluteUrlFileMixin, serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "file"]

# Output will convert `file` field to an absolute URL
serializer = DocumentSerializer(instance, context={"request": request})
data = serializer.data
```

#### Notes

- Works with both Django model serializers and custom serializers.
- Relative file paths are automatically converted to absolute URLs.
- Can manually specify fields via `file_fields` for non-model serializers.

### 9. BulkCreateMixin — API Reference

```python
from djresttoolkit.serializers.mixins import BulkCreateMixin
```

#### `BulkCreateMixin`

A **DRF serializer mixin** that adds support for:

- **Single instance creation** with extra context fields
- **Bulk creation** from a list of validated data dictionaries
- **Updating serializer field error messages** with model-specific messages

#### Bulk Create Mixin Notes

- `bulk_create()` does **not trigger model signals** or call `.save()` on instances.
- `Meta.model` **must** be defined in the serializer.

#### Bulk Create Mixin Methods

#### `create(self, validated_data: dict[str, Any] | list[dict[str, Any]]) -> Model | list[Model]`

- Creates single or multiple model instances.
- **Parameters:**
  - `validated_data`: dict for single instance or list of dicts for bulk creation.
  
- **Returns:**
  - Single model instance or list of instances.
  
- **Raises:**
  - `AttributeError` if `Meta.model` is not defined.
  - `NotImplementedError` if used with a serializer that does not implement `create()`.

#### `get_fields(self) -> dict[str, SerializerField]`

- Extends DRF serializer `get_fields()` to update **error messages** using model field definitions.
- **Returns:**
  - Dictionary of serializer fields.

- **Warning:**
  - Logs a warning if a serializer field is not present on the model.

### Bulk Create Mixin Example

```python
from rest_framework import serializers
from djresttoolkit.serializers.mixins import BulkCreateMixin
from myapp.models import Product

class ProductSerializer(BulkCreateMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]

# Single creation
serializer = ProductSerializer(data={"name": "Item1", "price": 10})
serializer.is_valid(raise_exception=True)
product = serializer.save()

# Bulk creation
serializer = ProductSerializer(
    data=[
        {"name": "Item2", "price": 20},
        {"name": "Item3", "price": 30},
    ],
    many=True
)
serializer.is_valid(raise_exception=True)
products = serializer.save()
```

#### Bulk Create Mixin Features

- Works seamlessly with DRF `ModelSerializer`.
- Automatically updates field error messages based on Django model definitions.
- Bulk creation is optimized using `model.objects.bulk_create()` for efficiency.

### 10. ModelChoiceFieldMixin — API Reference

```python
from djresttoolkit.models.mixins import ModelChoiceFieldMixin
```

### `ModelChoiceFieldMixin`

A **Django model mixin** to retrieve **choice fields** from a model, designed to work seamlessly with Django's `TextChoices`.

#### Class Attributes in Model Choice Field Mixin

- `model: type[Model] | None` — The Django model class to inspect. **Must be set.**
- `choice_fields: list[str] | None` — List of model field names that contain choices. **Must be set.**

#### Model Choice Field Mixin Methods

- `get_choices() -> dict[str, dict[str, str]]`

Retrieve the choice fields from the model as a dictionary.

- **Returns:**

  ```python
  {
      "field_name": {
          "choice_value": "Choice Label",
          ...
      },
      ...
  }
  ```

- **Raises:**

  - `AttributeDoesNotExist` — If `model` or `choice_fields` is not set.
  - `ChoiceFieldNotFound` — If a field does not exist, has no choices, or has invalid choice format.

---

### Model Choice Field Mixin Example

```python
from django.db import models
from djresttoolkit.serializers.mixins import ModelChoiceFieldMixin

class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    status = models.CharField(max_length=20, choices=Status.choices)
    category = models.CharField(max_length=50, choices=[
      ("a", "Category A"),
      ("b", "Category B"),
    ])

class ProductChoiceMixin(ModelChoiceFieldMixin):
    model = Product
    choice_fields = ["status", "category"]

choices = ProductChoiceMixin.get_choices()
print(choices)
# Output:
# {
#   "status": {"draft": "Draft", "published": "Published"},
#   "category": {"a": "Category A", "b": "Category B"}
# }
```

#### Features of Model Choice Field Mixin

- Safely validates that fields exist and have valid choices.
- Returns a ready-to-use dictionary mapping values to labels.
- Ideal for DRF serializers, forms, and admin customization.

Here’s a concise **docs entry** for your `ChoiceFieldsAPIView` suitable for `djresttoolkit` documentation:

---

### 11. ChoiceFieldsAPIView — API Reference

```python
from djresttoolkit.views import ChoiceFieldsAPIView
```

#### `ChoiceFieldsAPIView`

A **generic DRF API view** to return all choices for specified model fields.

#### Class Attributes of Choice Fields APIView

- `model_class: type[Model] | None` — The Django model to inspect. **Must be set.**
- `choice_fields: list[str] | None` — List of fields on the model with choices. **Must be set.**

---

#### Choice Fields APIView Methods

- `get(request: Request) -> Response`

Fetches the choices for the configured model fields.

- **Returns:**
  - `200 OK` — JSON object containing all choices:

    ```json
    {
        "choices": {
            "status": {"draft": "Draft", "published": "Published"},
            "category": {"a": "Category A", "b": "Category B"}
        }
    }
    ```

  - `400 Bad Request` — If any error occurs while retrieving choices.

- **Raises:**
  - `AttributeDoesNotExist` — If `model_class` or `choice_fields` is not set.

---

### Example of Choice Fields APIView

```python
from django.urls import path
from djresttoolkit.views import ChoiceFieldsAPIView
from myapp.models import Product

class ProductChoiceAPI(ChoiceFieldsAPIView):
    model_class = Product
    choice_fields = ["status", "category"]

urlpatterns = [
    path(
      "api/v1/product-choices/",
      ProductChoiceAPI.as_view(),
      name="product-choices"
    ),
]
```

#### Choice Fields APIView Features

- Dynamically returns all choices for selected fields in a model.
- Useful for frontend forms or API consumers that need selectable options.
- Integrates seamlessly with `ModelChoiceFieldMixin` from `djresttoolkit`.

### 12. RetrieveObjectMixin — API Reference

```python
from djresttoolkit.views.mixins import RetrieveObjectMixin
```

#### `RetrieveObjectMixin[T: Model]`

A **generic mixin** to retrieve a single Django model instance by filters.

#### Class Attributes of Retrieve Object Mixin

- `queryset: QuerySet[T] | None` — The queryset used to retrieve objects. **Must be set.**

#### Raises of Retrieve Object Mixin

- `QuerysetNotDefinedError` — If `queryset` is not set in the class.

#### Retrieve Object Mixin Methods

- `get_object(**filters: Any) -> T | None`

Retrieve a single model object using the provided filter criteria.

- **Parameters:**
  - `**filters` — Keyword arguments to filter the queryset (e.g., `id=1`, `slug="abc"`).

- **Returns:**
  - Model instance matching the filters, or `None` if no match is found.

#### Example of Retrieve Object Mixin

```python
from rest_framework.views import APIView
from django.http import JsonResponse
from myapp.models import Book
from djresttoolkit.mixins import RetrieveObjectMixin

class BookDetailView(RetrieveObjectMixin[Book], APIView):
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        book = self.get_object(id=kwargs["id"])
        if book:
            return JsonResponse({"title": book.title, "author": book.author})
        return JsonResponse({"detail": "Not found"}, status=404)
```

#### Features of Retrieve Object Mixin

- Simplifies object retrieval in class-based views or DRF views.
- Returns `None` instead of raising `DoesNotExist`, making error handling easier.
- Works with any Django model and queryset.

## 🛠️ Planned Features

- Add more utils

## 🤝 Contributing

Contributions are welcome! Please open an issue or PR for any improvements.

## 📜 License

MIT License — See [LICENSE](LICENSE).

## 👤 Author

For questions or assistance, contact **Shailesh** at [shaileshpandit141@gmail.com](mailto:shaileshpandit141@gmail.com).
