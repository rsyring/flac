import subprocess


class TestCLI:

    def test_hello(self, app):

        runner = app.test_cli_runner()

        result = runner.invoke('hello')
        assert 'Hello World!\n' == result.output

        result = runner.invoke('hello', 'flac users')
        assert 'Hello flac users!\n' == result.output

    def test_log(self, script_args):
        # Can't use the runner to test this because pytest hijacks the log output.  So, just
        # fork out a process to call the application like we would in a script.
        args = script_args + ['log']
        result = subprocess.run(args, capture_output=True)

        assert b'info log message' in result.stderr
        assert b'warning log message' in result.stderr
        assert b'debug' not in result.stderr

        args = script_args + ['--quiet', 'log']
        result = subprocess.run(args, capture_output=True)

        assert b'info log message' not in result.stderr

        args = script_args + ['--debug', 'log']
        result = subprocess.run(args, capture_output=True)

        assert b'debug log message' in result.stderr

    def test_sentry(self, script_args):
        args = script_args + ['--with-sentry', 'hello']
        result = subprocess.run(args, capture_output=True)

        assert b'sentry' not in result.stderr
