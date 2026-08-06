"""What your network allows, established without hanging your notebook.

Tier 2 by convention. Standard library only — it has to run before anything is
installed, on a machine that may not be able to install anything.

Week 1 Session 1 writes this probe from scratch, and Week 9's challenge re-runs
it against the environment the app will actually deploy into. That second use is
why it lives here: TC9's ecosystem checklist is the same questions asked of a
different network, and nobody should rewrite the probe to ask them.

**The hard deadline is the feature.** A serial probe on a locked-down corporate
network — which is the case this exists for — can hang for minutes, because
`socket.gethostbyname` does not honour `socket.setdefaulttimeout` and a
blackholed DNS query blocks until the system resolver gives up. A diagnostic
tool that hangs on exactly the machines it was written to diagnose is worse than
no tool, because the student concludes their environment is broken in some new
way and stops. Every probe here runs in a worker with a wall-clock deadline and
reports `timeout` rather than blocking.

**Naming the interceptor is the point.** "TLS succeeded" is not the interesting
result on a managed laptop. *Who signed it* is. A corporate proxy re-signs every
certificate with an internal CA, which is why `pip` works in the terminal and
fails inside a container that does not trust that CA — a Week 1 mystery that
becomes a Week 9 conversation.
"""

from __future__ import annotations

import os
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# Hosts every week of this course eventually needs.
DEFAULT_HOSTS: tuple[tuple[str, str], ...] = (
    ("pypi.org", "Python packages"),
    ("files.pythonhosted.org", "the actual wheel downloads"),
    ("api.openai.com", "the model API"),
    ("cdn.jsdelivr.net", "the CDN the Week 1 frontend uses"),
    ("huggingface.co", "open weights, Weeks 2 and 8"),
    ("registry-1.docker.io", "container images"),
    ("github.com", "this repository"),
)

# Issuer organisations that are public certificate authorities. Anything else
# signing a public site means something is terminating your TLS.
PUBLIC_CAS = (
    "digicert", "let's encrypt", "isrg", "google trust services", "amazon",
    "sectigo", "comodo", "globalsign", "cloudflare", "microsoft", "baltimore",
    "usertrust", "godaddy", "entrust", "identrust", "starfield", "verisign",
    "thawte", "geotrust", "rapidssl", "buypass", "actalis", "certum",
)

# Environment variables that reveal a proxy or a swapped trust store.
PROXY_VARS = (
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "no_proxy",
    "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS", "PIP_INDEX_URL", "PIP_TRUSTED_HOST",
    "UV_INDEX_URL", "UV_DEFAULT_INDEX",
)


@dataclass
class Probe:
    host: str
    why: str = ""
    ip: str | None = None
    dns_ok: bool = False
    tls_ok: bool = False
    issuer: str = ""
    error: str = ""

    @property
    def intercepted(self) -> bool:
        """True when a public site was signed by something that is not a public CA."""
        if not self.tls_ok or not self.issuer:
            return False
        low = self.issuer.lower()
        return not any(ca in low for ca in PUBLIC_CAS)

    @property
    def status(self) -> str:
        if not self.dns_ok:
            return "DNS BLOCKED"
        if not self.tls_ok:
            return "TLS BLOCKED"
        return "INTERCEPTED" if self.intercepted else "OK"


@dataclass
class Report:
    probes: list = field(default_factory=list)
    proxy_env: dict = field(default_factory=dict)

    @property
    def blocked(self) -> list:
        return [p for p in self.probes if not p.tls_ok]

    @property
    def intercepted(self) -> list:
        return [p for p in self.probes if p.intercepted]

    def __str__(self) -> str:
        bits = [f"{len(self.probes) - len(self.blocked)}/{len(self.probes)} reachable"]
        if self.intercepted:
            names = sorted({p.issuer for p in self.intercepted})
            bits.append(f"TLS intercepted by {', '.join(names)}")
        if self.proxy_env:
            bits.append(f"{len(self.proxy_env)} proxy/CA variables set")
        return " · ".join(bits)

    def verdict(self) -> str:
        """The sentence to paste into use_case/ecosystem.md."""
        if self.blocked:
            hosts = ", ".join(p.host for p in self.blocked)
            return (
                f"Blocked: {hosts}. Someone has to allow these or mirror them "
                f"internally before Weeks 2, 8, and 9 — find out who, now, not "
                f"in the week you need it."
            )
        if self.intercepted:
            names = ", ".join(sorted({p.issuer for p in self.intercepted}))
            return (
                f"TLS is terminated by {names}. Everything works in your terminal "
                f"because your OS trusts that CA. It will fail inside a container, "
                f"which does not — you will need that CA baked in or mounted. This "
                f"is a Week 9 conversation you can start now."
            )
        return "Open network, public CAs, no proxy. Nothing here will bite you."


def _one(host: str, why: str, timeout: float) -> Probe:
    probe = Probe(host=host, why=why)
    try:
        # getaddrinfo rather than gethostbyname: it is the modern call, it
        # returns IPv6 too, and the failure is a clean exception.
        info = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        probe.ip = info[0][4][0]
        probe.dns_ok = True
    except Exception as exc:
        probe.error = f"{type(exc).__name__}"
        return probe

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                probe.tls_ok = True
                cert = tls.getpeercert() or {}
                for field_ in cert.get("issuer", ()):
                    for key, value in field_:
                        if key == "organizationName":
                            probe.issuer = value
    except Exception as exc:
        probe.error = f"{type(exc).__name__}: {exc}"[:80]
    return probe


def check_egress(hosts=DEFAULT_HOSTS, *, timeout: float = 6.0,
                 workers: int = 8) -> Report:
    """Probe every host concurrently, with a wall-clock deadline per host.

    The deadline is enforced by `as_completed`, not by the socket, because DNS
    resolution ignores socket timeouts entirely — a blackholed lookup blocks
    until the system resolver gives up, which on a managed network can be tens
    of seconds. Worker threads that miss the deadline are abandoned; the process
    still exits because they are daemon threads in a pool we do not join.
    """
    report = Report()
    pending = {}
    pool = ThreadPoolExecutor(max_workers=min(workers, max(len(hosts), 1)))
    try:
        for host, why in hosts:
            pending[pool.submit(_one, host, why, timeout)] = (host, why)
        deadline = timeout * 2 + 2          # generous, but bounded
        done = set()
        try:
            for future in as_completed(list(pending), timeout=deadline):
                done.add(future)
                report.probes.append(future.result())
        except TimeoutError:
            pass
        for future, (host, why) in pending.items():
            if future not in done:
                future.cancel()
                report.probes.append(
                    Probe(host=host, why=why,
                          error=f"no answer within {deadline:.0f}s — treat as blocked")
                )
    finally:
        # Do not wait: a thread stuck in getaddrinfo cannot be interrupted, and
        # blocking here would reintroduce the hang this function exists to avoid.
        pool.shutdown(wait=False)

    order = {h: i for i, (h, _) in enumerate(hosts)}
    report.probes.sort(key=lambda p: order.get(p.host, 999))
    report.proxy_env = {k: os.environ[k] for k in PROXY_VARS if os.environ.get(k)}
    return report
