# Flac

Flask based library to help structure an application with an eye towards CLI apps, not just web.


## Features

- App factory pattern
    - blueprints (web & CLI)
- CLI Integration
    - custom command
    - two-phase init for blueprints
- Configuration
    - .env & .flaskenv
    - from files
    - from environment
    - alternate settings for testing, dev, prod
- Logging
    - logs are probably cheap, don't prematurely optimize
    - centralize your logs to an aggregation service
    - .info logs are show/saved by default
    - cli output is plain text
    - saved logs are JSON
    - saved logs go to syslog, let devops handle the aggregation
- Testing
    - alternate DB URI
    - pytest & fixtures
- Flask-SQLAlchemy
    - ext init
    - fixtures to get db to ensure app context
- Celery
    - refresh process pool


- cli integration with the ability to customize the app's configuration using global cli options

    someapp --debug --with-sentry run-some-task

- pytest fixtures for app initialization
- demo cli test that uses separate process

## Develoment

### Copier Template

Project structure and tooling mostly derives from the [Coppy](https://github.com/level12/coppy),
see its documentation for context and additional instructions.

This project can be updated from the upstream repo, see
[Updating a Project](https://github.com/level12/coppy?tab=readme-ov-file#updating-a-project).

### Project Setup

From zero to hero (passing tests that is):

1. Ensure [host dependencies](https://github.com/level12/coppy/wiki/Mise) are installed

2. Start docker service dependencies (if applicable):

   `docker compose up -d`

3. Sync [project](https://docs.astral.sh/uv/concepts/projects/) virtualenv w/ lock file:

   `uv sync`

4. Configure pre-commit:

   `pre-commit install`

5. Run tests:

   `nox`

### Versions

Versions are date based.  A `bump` action exists to help manage versions:

```shell

  # Show current version
  mise bump --show

  # Bump version based on date, tag, and push:
  mise bump

  # See other options
  mise bump -- --help
```
