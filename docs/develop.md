
## Running formatters

Run black last, it has the final say in formatting (and does not always agree with others).

```sh
poetry run isort .
poetry run black .
poetry run flake8 .
```
