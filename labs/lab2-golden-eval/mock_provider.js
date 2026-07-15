// 教學用 mock provider：回放 fixtures/llm_responses.json 的預錄回應（零 API key）。
//
// 與 app/llm_client.py 的 FakeLLMClient 遵守同一條規則：
// 渲染後的 prompt 含關鍵約束句「配料只能使用菜單」→ 回放 good 變體；
// 否則回放 sloppy 變體——用來模擬「prompt 品質影響輸出品質」的回歸情境。
// （這是教學模擬器；真實世界的 prompt 評測請對真模型跑，見 /live-eval 加分關。）
const fs = require('fs');
const path = require('path');

const FIXTURES = JSON.parse(
  fs.readFileSync(
    path.join(__dirname, '..', '..', 'fixtures', 'llm_responses.json'),
    'utf8'
  )
);
const PROMPT_QUALITY_MARKER = '配料只能使用菜單';

class MockBobaProvider {
  constructor(options) {
    this.providerId = (options && options.id) || 'mock-boba-llm';
  }

  id() {
    return this.providerId;
  }

  async callApi(prompt, context) {
    const input =
      context && context.vars ? String(context.vars.input || '') : '';
    const entry = FIXTURES[input] || FIXTURES.__default__;
    const variant = prompt.includes(PROMPT_QUALITY_MARKER) ? 'good' : 'sloppy';
    const payload = entry[variant] !== undefined ? entry[variant] : entry.good;
    const output =
      typeof payload === 'string' ? payload : JSON.stringify(payload);
    return { output };
  }
}

module.exports = MockBobaProvider;
