import json
import hashlib
from pathlib import Path


class AuthManager:
    def __init__(self) -> None:
        self._path = Path.home() / ".sv200x_agc_avc" / "users.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._users: dict[str, str] = {}
        self._load()

    def _hash(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                self._users = {k: v for k, v in data.items() if isinstance(v, str)}
            except (json.JSONDecodeError, OSError):
                self._users = {}
        if "admin" not in self._users:
            self._users["admin"] = self._hash("123456")
            self._save()

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._users, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def login(self, username: str, password: str) -> tuple[bool, str]:
        username = username.strip()
        if not username or not password:
            return False, "账号和密码不能为空"
        stored = self._users.get(username)
        if stored is None:
            return False, "账号不存在"
        if stored != self._hash(password):
            return False, "密码错误"
        return True, "登录成功"

    def register(self, username: str, password: str, confirm: str) -> tuple[bool, str]:
        username = username.strip()
        if not username or not password:
            return False, "账号和密码不能为空"
        if len(username) < 3:
            return False, "账号长度至少3个字符"
        if len(password) < 6:
            return False, "密码长度至少6个字符"
        if password != confirm:
            return False, "两次输入的密码不一致"
        if username in self._users:
            return False, "该账号已存在"
        self._users[username] = self._hash(password)
        self._save()
        return True, "注册成功，请登录"
