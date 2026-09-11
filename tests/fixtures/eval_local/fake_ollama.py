"""假 Ollama：daemon 看起來活著，但每次推論都失敗。

用來重現 `output_provider_error.json` 那一份 fixture——也就是
`summarize_eval.js` 存在的理由：`/api/tags` 回 200（所以 workflow 的
「daemon 還活著嗎」那道檢查會通過），`/api/chat` 回 404 model not found。
在這個狀態下 promptfoo 仍會正常結束並寫出完全合法的 output.json。

用法（重產 fixture 的完整步驟見同目錄 README.md）：

    python3 tests/fixtures/eval_local/fake_ollama.py &
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 11434
MODEL_NOT_FOUND = 'model "qwen2.5:1.5b" not found, try pulling it first'


class FakeOllamaHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    # 方法名由 BaseHTTPRequestHandler 的介面決定，不能改成 snake_case
    def do_GET(self):
        if self.path.startswith("/api/tags"):
            self._send(200, {"models": []})
        elif self.path == "/":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        self._send(404, {"error": MODEL_NOT_FOUND})

    def log_message(self, *args):
        """安靜一點：重產 fixture 時不需要 access log。"""


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), FakeOllamaHandler).serve_forever()
