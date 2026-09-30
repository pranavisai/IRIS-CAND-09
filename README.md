# Portable Dockerized Pilot Runtime (IRIS-CAND-09)

A small, Dockerized, country-aware pilot runtime using Python, PostgreSQL and PostGIS.

## Submission checklist

| Requirement                                                                   | Status | Notes                                                                                                                             |
| ----------------------------------------------------------------------------- | :----: | --------------------------------------------------------------------------------------------------------------------------------- |
| README: setup, assumptions, commands, and architecture choices                |   [x]  | Documented Docker setup, environment configuration, architecture, migrations, testing and runtime commands.                        |
| Automated tests covering the highest-risk correctness conditions              |   [x]  | Includes configuration and input validation tests. Smoke tests verify database connectivity, PostGIS and stored records.          |
| A small deterministic fixture set committed with the submission               |   [x]  | Includes a synthetic GeoJSON fixture with three sample sites for repeatable testing.                                              |
| No production secrets, paid APIs, or inaccessible proprietary data            |   [x]  | Uses local configuration and generated data. No production credentials or paid APIs are required.                         |
| Document any deliberate simplification and how it would evolve for production |   [x]  | Documented the local GeoJSON adapter. |

## 1. Overview

This project demonstrates a portable runtime for processing geospatial site data.

**Features:**

* PostgreSQL 16 with PostGIS 3.4
* A Python 3.12+ worker
* Environment-based country and region configuration
* A modular data adapter interface
* GeoJSON input validation
* Database migrations
* Spatial data storage using EPSG:4326
* Smoke and unit tests

The pilot uses a small, synthetic GeoJSON fixture. It does not depend on a live external data source, keeping it easy to reproduce.

## 2. Architecture

The application consists of two Docker services:

* `db`: PostgreSQL with PostGIS enabled.
* `worker`: Loads data through an adapter, validates it, applies migrations and inserts site records.

The worker depends on the database health check succeeding before it starts.


### Data adapter architecture

Data ingestion is separated from the main processing pipeline through a simple adapter.

* `app/adapters/base.py`: Defines the `DataAdapter` interface.
* `app/adapters/geojson.py`: Implements the interface for reading local GeoJSON FeatureCollections.
* `app/worker.py`: Uses the adapter to load features, validate them and store the resulting records.

This separation allows creation of additional data adapters without changing the core database logic.

## 3. Requirements

The host machine needs:

* Docker Engine or Docker Desktop
* Docker Compose v2
* Internet access for the initial image pull

The Docker images must be compatible with the host architecture. Docker may use emulation on ARM hosts.

## 4. Configuration and Data Ingestion

The application is configured using environment variables. No `.env` files or production credentials are committed.

| Variable          | Description                  |
| ----------------- | ---------------------------- |
| `COUNTRY_CODE`    | Two-letter country code      |
| `REGION_CODE`     | Region identifier            |
| `SOURCE_ENDPOINT` | GeoJSON fixture path         |
| `DB_NAME`         | Database name                |
| `DB_USER`         | Database user                |
| `DB_PASSWORD`     | Database password            |
| `DB_HOST`         | Database hostname            |
| `DB_PORT`         | Database port inside Compose |
| `OUTPUT_PATH`     | Worker output directory      |

Two example configurations are provided:

* `.env.dev.example` — Germany
* `.env.second-host.example` — France

### Germany

Create the local configuration:

```bash
cp .env.dev.example .env
```

Build the worker image and start the database:

```bash
docker compose build
docker compose up -d db
```

Wait until the database reports `healthy`:

```bash
docker compose ps
```

Run the worker:

```bash
docker compose run --rm worker
```

This loads the German pilot data into PostgreSQL.

### France

To load the French fixture into the **same database on the same host**, switch the country-specific configuration:

```bash
cp .env.second-host.example .env
```

Ensure that `DB_NAME`, `DB_USER`, and `DB_PASSWORD` match the existing database configuration. The French settings should be:

```dotenv
COUNTRY_CODE=FR
REGION_CODE=IDF
SOURCE_ENDPOINT=fixtures/sites_fr.geojson
```

Do not delete the database volume or recreate the database when switching countries.

Run the worker:

```bash
docker compose run --rm worker
```

This loads the French pilot data alongside the existing German records.

The second-host template can also be used on a separate host, but that host will have its own database unless explicitly configured to connect to a shared database.

### Verify loaded data

```bash
docker compose exec db sh -c \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
-c "SELECT country_code, region_code, COUNT(*) AS site_count FROM sites GROUP BY country_code, region_code ORDER BY country_code;"'
```

Expected result after loading both fixtures into the same database:

```text
 country_code | region_code | site_count
--------------+-------------+-----------
 DE           | NW          |     3
 FR           | IDF         |     3
```

## 5. Start the application

For a fresh installation, follow the configuration and startup instructions in Section 4. The environment file must be created before the database is initialized.

To inspect the running services and database logs:

```bash
docker compose ps
docker compose logs db
```

To stop the application:

```bash
docker compose down
```

To remove the database volume and all stored data (for a complete reset):

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes the local database data.

### Worker responsibilities

1. Loads the application configuration.
2. Applies pending database migrations.
3. Loads the configured source through the GeoJSON adapter.
4. Validates the input records against the configured country and region.
5. Inserts or updates the records in PostgreSQL.
6. Writes a processing summary.

## 6. Smoke test

Run the smoke test with:

```bash
docker compose run --rm worker python -m app.smoke_test
```

It checks that:

* PostGIS is available.
* Records exist for the configured country and region.
* The records have valid geometry storage.
* The geometry SRID is 4326.

The smoke test expects the worker to have populated the database first.

## 7. Unit tests

Run the tests inside Docker:

```bash
docker compose build worker
docker compose run --rm worker pytest -v
```

## 8. Output

The worker writes its summary to:

```text
output/summary.json
```

The output includes:

* Configured country and region
* Source endpoint
* Number of processed records
* Processing status

The output directory is mounted from the host, so the generated summary remains available after the worker container exits.

## 9. Database migrations

SQL migration files are stored in `migrations/`.

Migrations are applied in filename order. The `schema_migrations` table records applied files, so previously applied migrations are skipped on subsequent runs.

The initial migration creates the `sites` table, enables PostGIS and adds spatial and country-region indexes.

## 10. Spatial data

The canonical geometry column is `geom`.

Input GeoJSON coordinates are interpreted as longitude and latitude in WGS 84 (EPSG:4326).

Spatial indexing is provided by a GiST index. Coordinates are stored in degrees. Any future distance or area calculations must use an appropriate projected CRS or geodesic calculations.

## 11. Security considerations

The pilot runtime includes the following security measures:

1. Secret management: Actual .env files are excluded from version control and the Docker build context. Example files contain placeholders only.
2. Non-root execution: The Python worker runs as an unprivileged iris user inside the container.
3. Database isolation: PostgreSQL is not exposed through a published host port. The worker accesses it through the internal Docker network.
4. Read-only fixtures: The input fixture directory is mounted read-only inside the worker container.
5. Dependency auditing: Python dependencies are version-pinned, and ```pip-audit``` is used to check for known vulnerabilities.
6. Restricted filesystem access: The worker has write permissions for its output and log directories rather than the entire application directory.

### Production considerations

Before production deployment, additional measures that can be taken:

1. Managing credentials through a secrets manager or Docker secrets.
2. Configuring database backups and recovery procedures.
3. Enforcing appropriate network restrictions and database permissions.
4. Regularly rebuilding images and reviewing dependency vulnerabilities.
5. Centralizing logs and monitoring application failures.
