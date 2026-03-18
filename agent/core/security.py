import os, sys, hashlib, json, sqlite3, base64, logging
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

log = logging.getLogger(__name__)
_INSECURE_DEFAULT = "aegis-default-dev-key-change-in-prod"
_DATA_ROOT = Path("/app/data").resolve()


class SecretsManager:
    def __init__(self):
        self.backend = os.getenv("SECRET_BACKEND", "env")
        self._cache = {}

    def get(self, key: str) -> str:
        if key in self._cache:
            return self._cache[key]
        if self.backend == "vault":
            try:
                import hvac
                client = hvac.Client(
                    url=os.getenv("VAULT_ADDR", "http://vault:8200"),
                    token=os.getenv("VAULT_TOKEN")
                )
                resp = client.secrets.kv.v1.read_secret(path=key)
                val = resp["data"]["value"]
                self._cache[key] = val
                return val
            except Exception as e:
                print(f"Vault miss for {key}: {e} - falling back to env")
        val = os.getenv(key, "")
        if val:
            self._cache[key] = val
        return val


class EncryptedMemory:
    def __init__(self, db_path: str = "/app/data/memory.db"):
        resolved = Path(db_path).resolve()
        if not str(resolved).startswith(str(_DATA_ROOT)):
            raise ValueError(f"Invalid db_path outside data directory: {db_path}")
        self.db_path = str(resolved)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        key = os.getenv("MEMORY_MASTER_KEY", "")
        if not key or key == _INSECURE_DEFAULT or key.startswith("change-me"):
            msg = (
                "FATAL: MEMORY_MASTER_KEY is not set or is insecure.\n"
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\"\n"
                "Then set it in your .env file."
            )
            print(msg, file=sys.stderr)
            sys.exit(1)
        self.master = key.encode()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_hash TEXT NOT NULL,
                    encrypted_content BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_user ON memories(user_hash)"
            )

    def _fernet(self, user_id: str) -> Fernet:
        derived = hashlib.scrypt(
            self.master, salt=user_id.encode(),
            n=2**14, r=8, p=1, dklen=32
        )
        return Fernet(base64.urlsafe_b64encode(derived))

    def save(self, user_id: str, content: str):
        f = self._fernet(user_id)
        enc = f.encrypt(content.encode())
        uhash = hashlib.sha256(user_id.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as c:
            c.execute(
                "INSERT INTO memories (user_hash, encrypted_content) VALUES (?,?)",
                (uhash, enc)
            )

    def recall(self, user_id: str, limit: int = 5) -> list:
        uhash = hashlib.sha256(user_id.encode()).hexdigest()
        f = self._fernet(user_id)
        with sqlite3.connect(self.db_path) as c:
            rows = c.execute(
                "SELECT encrypted_content FROM memories "
                "WHERE user_hash=? ORDER BY created_at DESC LIMIT ?",
                (uhash, limit)
            ).fetchall()
        out = []
        for (blob,) in rows:
            try:
                out.append(f.decrypt(blob).decode())
            except Exception as e:
                log.warning("Failed to decrypt memory blob: %s", e)
        return out

    def purge(self, user_id: str):
        uhash = hashlib.sha256(user_id.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as c:
            c.execute("DELETE FROM memories WHERE user_hash=?", (uhash,))


class AuditLogger:
    def __init__(self, path: str = "/app/data/audit.jsonl"):
        resolved = Path(path).resolve()
        if not str(resolved).startswith(str(_DATA_ROOT)):
            raise ValueError(f"Invalid audit path outside data directory: {path}")
        self.path = str(resolved)
        resolved.parent.mkdir(parents=True, exist_ok=True)

    def log(self, user_id: str, tool: str, decision: str,
            reason: str, status: str, channel: str, session_id: str):
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_hash": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "tool": tool,
            "decision": decision,
            "reason": reason,
            "status": status,
            "channel": channel,
            "session_id": session_id,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")


secrets = SecretsManager()
memory_store = EncryptedMemory()
audit = AuditLogger()