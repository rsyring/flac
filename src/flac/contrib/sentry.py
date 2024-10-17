import sentry_sdk


def init_sentry(app, **kwargs):
    assert not app.testing, 'Sentry should not be enabled during testing.'
    sentry_dsn = app.config.get('SENTRY_DSN')
    if not sentry_dsn:
        raise ValueError('Sentry DSN expected but not configured.')

    sentry_sdk.init(sentry_dsn, **kwargs)
