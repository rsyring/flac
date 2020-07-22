Features
--------

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

- pytest fixtures for app initialization?
- demo cli test that uses separate process


Notes:
-----------

Different ways to initialize the app:

- cli
- wsgi
- celery
- tests


TODO:
-----------

- test db-init command and related database lib function
