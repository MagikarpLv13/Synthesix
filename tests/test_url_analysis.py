import hashlib
import unittest
from email.message import Message
from io import BytesIO

from analysis.urls import MAX_HASH_BYTES, analyze_url
from exceptions import UrlAnalysisError


def public_resolver(host, port, *, type):
    return [(2, type, 6, "", ("93.184.216.34", port))]


def private_resolver(host, port, *, type):
    return [(2, type, 6, "", ("127.0.0.1", port))]


class FakeResponse:
    def __init__(self, url, status, body=b"", headers=None):
        self._url = url
        self.status = status
        self._body = BytesIO(body)
        self.headers = Message()
        for name, value in (headers or {}).items():
            self.headers[name] = value

    def getcode(self):
        return self.status

    def geturl(self):
        return self._url

    def read(self, size=-1):
        return self._body.read(size)

    def close(self):
        self._body.close()


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request.full_url, timeout))
        return self.responses.pop(0)


class UrlAnalysisTestCase(unittest.TestCase):
    def test_records_redirect_headers_tracking_and_content_hash(self):
        body = b"public response"
        opener = FakeOpener(
            [
                FakeResponse(
                    "https://example.com/start",
                    302,
                    headers={"Location": "/final?utm_source=test&id=42"},
                ),
                FakeResponse(
                    "https://example.com/final?utm_source=test&id=42",
                    200,
                    body,
                    headers={
                        "Content-Type": "text/plain",
                        "Content-Length": str(len(body)),
                        "Content-Security-Policy": "default-src 'none'",
                        "Set-Cookie": "secret=value",
                    },
                ),
            ]
        )

        result = analyze_url(
            "https://example.com/start",
            opener=opener,
            resolver=public_resolver,
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.redirects), 1)
        self.assertEqual(result.redirects[0].status_code, 302)
        self.assertEqual(result.tracking_parameters, ("utm_source",))
        self.assertEqual(result.cleaned_url, "https://example.com/final?id=42")
        self.assertEqual(result.content_sha256, hashlib.sha256(body).hexdigest())
        self.assertEqual(
            result.headers["content-security-policy"],
            "default-src 'none'",
        )
        self.assertNotIn("set-cookie", result.headers)

    def test_rejects_private_destination_before_request(self):
        opener = FakeOpener([])

        with self.assertRaises(UrlAnalysisError):
            analyze_url(
                "http://localhost/admin",
                opener=opener,
                resolver=private_resolver,
            )

        self.assertEqual(opener.requests, [])

    def test_skips_hash_when_declared_content_is_too_large(self):
        opener = FakeOpener(
            [
                FakeResponse(
                    "https://example.com/archive",
                    200,
                    headers={"Content-Length": str(MAX_HASH_BYTES + 1)},
                )
            ]
        )

        result = analyze_url(
            "https://example.com/archive",
            opener=opener,
            resolver=public_resolver,
        )

        self.assertTrue(result.content_truncated)
        self.assertEqual(result.content_sha256, "")
        self.assertEqual(result.bytes_read, 0)

    def test_normalizes_international_hostname_and_path(self):
        opener = FakeOpener(
            [
                FakeResponse(
                    "https://xn--bcher-kva.example/%C3%A9tude",
                    200,
                )
            ]
        )

        result = analyze_url(
            "https://bücher.example/étude",
            opener=opener,
            resolver=public_resolver,
        )

        self.assertEqual(
            opener.requests[0][0],
            "https://xn--bcher-kva.example/%C3%A9tude",
        )
        self.assertEqual(result.final_domain_unicode, "bücher.example")
        self.assertEqual(
            result.final_domain_punycode,
            "xn--bcher-kva.example",
        )


if __name__ == "__main__":
    unittest.main()
