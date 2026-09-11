// eval-local 的結果判讀：把 promptfoo 的 output.json 讀成一段 GitHub step summary。
//
// 為什麼抽成獨立檔案、而不是寫在 workflow 的 run block 裡：那段 shell 只有真的
// 在 CI 上跑一次（要有 Ollama、要拉模型、要好幾分鐘 CPU 推論）才會被執行，
// 判讀邏輯寫錯時沒有任何守門會紅——而它印出來的那句話，正是讀者唯一會看到的
// 結論。抽出來之後 tests/test_eval_summary.py 就能拿真實的 output.json 餵它。
//
// 「只探測 daemon 存活」不足以區分「執行期錯誤」與「模型答錯」，這件事原本就
// 寫在 workflow 的註解裡；但原本的第二道防線（output.json 存在且能 parse）
// 一樣擋不住。**實測（2026-09-11、promptfoo 0.121.19，用一個對 /api/tags 回
// 200、對 /api/chat 回 404 "model not found" 的假 Ollama）**：
//   - promptfoo 正常跑完（exit 100）並寫出完全合法的 output.json；
//   - 三筆結果的 `response.output` 全是空字串；
//   - `stats.errors` 是 **0**，`failureReason` 是 ASSERT（斷言判 false），
//     整份檔案裡沒有任何 error 欄位。
// 也就是說「找 error／failureReason=ERROR 的列」這種直覺修法也是假守門。
// 分得出來的訊號只有一個：**沒有任何一筆拿到非空的模型輸出**。
//
// 用法：node summarize_eval.js [output.json]；markdown 印到 stdout。
// 一律以 0 結束——這支程式負責「講清楚發生什麼事」，紅不紅由 workflow 拿
// promptfoo 自己的離開碼決定。
'use strict';

const fs = require('fs');

const OUTPUT_PATH = process.argv[2] || 'output.json';
const MODEL = process.env.MODEL || '未知模型';

/** 讀 output.json，回傳 {kind:'unreadable', detail} 或 {kind:'ok', rows, stats}。 */
function readResults(path) {
  let raw;
  try {
    raw = fs.readFileSync(path, 'utf8');
  } catch (e) {
    return { kind: 'unreadable', detail: `讀不到 ${path}（${e.code || e.message}）` };
  }
  if (raw.trim() === '') {
    return { kind: 'unreadable', detail: `${path} 是空檔` };
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    return { kind: 'unreadable', detail: `${path} 不是合法 JSON（${e.message}）` };
  }
  const results = data && data.results;
  const rows = results && Array.isArray(results.results) ? results.results : null;
  if (rows === null) {
    return { kind: 'unreadable', detail: `${path} 裡找不到 results.results 陣列` };
  }
  if (rows.length === 0) {
    return { kind: 'unreadable', detail: `${path} 一筆結果都沒有` };
  }
  // 結果列不是物件時寧可整份判成讀不懂，也不要讓下面的取值拋 TypeError：
  // 這支程式崩掉＝step summary 一個字都沒有，比印錯話更難查。
  const badRow = rows.findIndex((row) => row === null || typeof row !== 'object');
  if (badRow !== -1) {
    return { kind: 'unreadable', detail: `${path} 第 ${badRow + 1} 筆結果不是物件` };
  }
  const stats = results.stats && typeof results.stats === 'object' ? results.stats : {};
  return { kind: 'ok', rows, stats };
}

/** 這一筆有沒有真的拿到模型輸出？空字串／純空白／缺欄位都算沒有。 */
function answered(row) {
  const output = row && row.response && row.response.output;
  if (typeof output === 'string') {
    return output.trim() !== '';
  }
  // 非字串輸出（provider 直接回物件／陣列）也算作答；null／undefined 不算。
  return output !== undefined && output !== null;
}

function summarize(path) {
  const parsed = readResults(path);
  const lines = [];

  if (parsed.kind === 'unreadable') {
    lines.push('### ⚠️ eval-local 未完成——執行期錯誤，不是模型品質訊號');
    lines.push('');
    lines.push('promptfoo 沒有產出可解析的結果檔，代表評測根本沒跑完——多半是');
    lines.push('config／provider 設定錯誤，而不是小模型答錯。');
    lines.push('');
    lines.push(`診斷：${parsed.detail}`);
    lines.push('');
    lines.push('請看上方 promptfoo 的錯誤輸出，**不要**把這次的紅當成模型品質訊號。');
    return lines.join('\n');
  }

  const { rows, stats } = parsed;
  const total = rows.length;
  const answeredCount = rows.filter(answered).length;
  const errorCount = Number.isFinite(Number(stats.errors)) ? Number(stats.errors) : 0;

  if (answeredCount === 0) {
    lines.push('### ⚠️ eval-local 未完成——執行期錯誤，不是模型品質訊號');
    lines.push('');
    lines.push(`${total} 題**全部沒有拿到模型輸出**（promptfoo 記錄的 errors＝${errorCount}）。`);
    lines.push('Ollama 的服務還活著，但模型沒有真的作答——多半是模型沒拉到、載入');
    lines.push('失敗（OOM）或請求被拒。這種情況下 promptfoo 仍會寫出合法的結果檔、');
    lines.push('把每一題記成斷言失敗，看起來就像「小模型全答錯」。');
    lines.push('');
    lines.push('**不要**把這次的紅當成小模型的品質訊號，請重跑。');
    return lines.join('\n');
  }

  const passed = rows.filter((row) => row.success === true).length;
  lines.push(`### 🏠 eval-local 完成（${MODEL} @ CI runner CPU）`);
  lines.push('');
  lines.push(`- **本次成績：${passed}/${total}**`);
  lines.push('- 零 API key、零外部帳號、零費用——模型就跑在 runner 上');
  lines.push('- 這是 **monitor** 不是 gate：紅色是資訊，不擋部署');
  lines.push(`- 考的是 golden 題庫的 ${total} 題小樣卷（主線 golden 軌為 6 題）`);
  lines.push(`- 對照組：雲端 gpt-4o-mini 曾以這 ${total} 題拿 3/3（2026-07-15 實測）`);
  lines.push('  （但書：3/3 那次跑的是舊版單行斷言，本次跑的是現在的防禦性斷言，');
  lines.push(`  兩次的擷取邏輯不同；而且 ${total} 題的樣本小到單題翻面就是 33 個百分點。`);
  lines.push('  這個對照足以說明「同一份 golden 可以換模型重考」，但不是精確的模型能力量測。）');
  if (answeredCount < total) {
    lines.push('');
    lines.push(`> ⚠️ 其中 ${total - answeredCount} 題沒有拿到任何模型輸出，那幾題的紅`);
    lines.push('> 不是答錯而是沒答到，請別計入模型品質。');
  }
  return lines.join('\n');
}

if (require.main === module) {
  process.stdout.write(`${summarize(OUTPUT_PATH)}\n`);
}

module.exports = { summarize, answered, readResults };
