# Unprinted receipts service

---

## What is this service for?

This service is intended for identifying orders without printed receipts for the current moment.

---

## How does the service work?

Check in wiki: https://github.com/goretsky-integration/unprinted-receipts/wiki/How-does-the-service-work

---

## Loggers

- auth_credentials_fetcher.
- auth_credentials_connection.
- dodo_is_connection.
- parser.

---

## Setup and run the service

### 1. Clone the repository

### 2. Create poetry virtual environment

```shell
poetry env use python3.11
```

### 3. Activate it

```shell
poetry shell
```

### 4. Install dependencies

```shell
poetry install --without dev
```

### 5. Create and set up application config file

```shell
cp config.example.toml config.toml
```

### 6. Create and set up logging config file

```shell
cp logging_config.example.json logging_config.json
```

### 7. Create and set up the units file

```shell
touch units.json
```

### 8. Run the service

```shell
python src/main.py
```
