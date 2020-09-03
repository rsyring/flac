
class TestViews:

    def test_hello(self, web):
        resp = web.get('/')
        assert resp.data == b'Hello World!'
