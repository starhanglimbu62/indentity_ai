---
applyTo: "apps/**/*.py,config/**/*.py"
---

# Django rules

Use Django 5.x patterns and Django REST Framework.

## Models

- Keep models focused on data and simple invariants.
- Put complex business logic in services.py.

## Views

- Keep views thin.
- Validate input using serializers.
- Call service functions.

## Services

- Services contain business operations.
- Use @transaction.atomic where multiple related database changes must succeed together.
- Services must not depend on HTTP request objects.

## URLs

- Use explicit route names.
- Keep URL structure predictable.

## Authentication

- Use JWT authentication through SimpleJWT.
- Do not bypass permission classes.

## Database

- Always use the Django ORM.
- Use select_related and prefetch_related where appropriate.
- Avoid N+1 queries.

## Migrations

After model changes run:

python manage.py makemigrations
python manage.py migrate

## Validation

Run:

python manage.py check
python manage.py test
