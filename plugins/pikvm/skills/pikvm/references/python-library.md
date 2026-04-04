# PiKVM Python Library: Implementation Patterns

## Architecture

```
pikvm/
├── __init__.py          # PiKVMClient export
├── client.py            # Main client class (auth, session, base request methods)
├── auth.py              # Authentication (session tokens, X-headers, TOTP)
├── msd.py               # Mass Storage Drive operations
├── atx.py               # ATX power management
├── hid.py               # Keyboard/mouse input
├── streamer.py          # Video stream, snapshots, OCR
├── gpio.py              # GPIO channel control
├── switch.py            # Multi-port KVM switch
├── redfish.py           # DMTF Redfish interface
├── websocket.py         # WebSocket event monitoring
├── exceptions.py        # Custom exception hierarchy
├── models.py            # Pydantic/dataclass response models
└── py.typed             # PEP 561 marker
```

## Core Client

```python
import httpx
import logging

class PiKVMClient:
    def __init__(self, host: str, user: str, passwd: str,
                 totp_secret: str | None = None,
                 verify_ssl: bool = False,
                 timeout: float = 30.0):
        self._base_url = f"https://{host}"
        self._user = user
        self._passwd = passwd
        self._totp_secret = totp_secret
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._logger = logging.getLogger(f"pikvm.{host}")
        self._client: httpx.AsyncClient | None = None

        # Subsystem accessors
        self.msd = MSDClient(self)
        self.atx = ATXClient(self)
        self.hid = HIDClient(self)
        self.streamer = StreamerClient(self)
        self.gpio = GPIOClient(self)
```

## Authentication Pattern

```python
def _get_auth_headers(self) -> dict[str, str]:
    password = self._passwd
    if self._totp_secret:
        import pyotp, time
        totp = pyotp.TOTP(self._totp_secret)
        now = int(time.time())
        remaining = totp.interval - (now % totp.interval)
        if remaining < 2:
            time.sleep(remaining + 1)
        password += totp.now()
    return {"X-KVMD-User": self._user, "X-KVMD-Passwd": password}
```

## Request Pattern with Logging

```python
async def _request(self, method: str, path: str,
                   params: dict | None = None,
                   data: bytes | None = None,
                   stream: bool = False) -> dict:
    url = f"{self._base_url}{path}"
    self._logger.debug("%s %s params=%s", method, path, params)

    response = await self._client.request(
        method, url, params=params, content=data,
        headers=self._get_auth_headers()
    )

    if response.status_code == 401:
        raise PiKVMAuthError("Not authenticated")
    if response.status_code == 403:
        raise PiKVMAuthError("Invalid credentials")
    if response.status_code == 409:
        raise PiKVMBusyError("Device busy")

    result = response.json()
    if not result.get("ok"):
        error = result.get("result", {})
        raise PiKVMAPIError(error.get("error", "Unknown"),
                            error.get("error_msg", ""))
    return result.get("result", {})
```

## ISO Upload with Progress

```python
async def upload_iso(self, image_name: str, file_path: Path,
                     progress_callback: Callable | None = None) -> None:
    self._logger.info("Uploading %s (%s bytes)", image_name, file_path.stat().st_size)
    total = file_path.stat().st_size
    uploaded = 0

    async def _stream():
        nonlocal uploaded
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                uploaded += len(chunk)
                if progress_callback:
                    progress_callback(uploaded, total)
                yield chunk

    await self._client.post(
        f"{self._base_url}/api/msd/write",
        params={"image": image_name},
        content=_stream(),
        headers=self._get_auth_headers(),
    )
    self._logger.info("Upload complete: %s", image_name)
```

## Exception Hierarchy

```python
class PiKVMError(Exception): ...
class PiKVMAuthError(PiKVMError): ...     # 401/403
class PiKVMBusyError(PiKVMError): ...     # 409 Conflict
class PiKVMAPIError(PiKVMError):           # Generic API error
    def __init__(self, error_type: str, message: str): ...
class PiKVMConnectionError(PiKVMError): ...  # Network failures
class PiKVMUnavailableError(PiKVMError): ... # 503
```

## Dependencies

- `httpx` — async HTTP client (preferred over aiohttp/requests)
- `pyotp` — TOTP 2FA support (optional)
- `pydantic` — response model validation (optional)
- `websockets` — WebSocket event monitoring (optional)
