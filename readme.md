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

Project structure and tooling mostly derives from the [copier-py-package](https://github.com/level12/copier-py-package),
see its documentation for context and additional instructions.

This project can be updated from the upstream repo, see [updates](https://github.com/level12/copier-py-package?tab=readme-ov-file#updates)

### Project Setup

From zero to hero (passing tests that is):

1. Ensure host dependencies are installed:

  - [reqs](https://github.com/level12/reqs): for virtualenv python deps
  - [mise](https://mise.jdx.dev/): for everything else, e.g. terraform, npm

2. Start docker service dependencies (if applicable):

   `docker compose up -d`

3. Run tests:

   `nox`

4. Use mise to activate the virtualenv for local dev

5. Install deps in active virtualenv:

    - `reqs bootstrap`
    - `reqs sync`

6. Configure pre-commit:

   `pre-commit install`


### Versions

Versions are date based.  Tools:

- Current version: `hatch version`
- Bump version based on date, tag, push: `mise run bump`
   - Options: `mise run bump -- --help`
