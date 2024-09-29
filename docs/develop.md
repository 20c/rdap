
## Running formatters

Run black last, it has the final say in formatting (and does not always agree with others).

```sh
pre-commit run --all-files
# or, if it's not installed
# uv run pre-commit run --all-files
```
