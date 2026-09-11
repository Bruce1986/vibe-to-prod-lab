// eval-local 的結果判讀：把 promptfoo 的 output.json 讀成一段 GitHub step summary。
//
// 為什麼抽成獨立檔案、而不是寫在 workflow 的 run block 裡：那段 shell 只有真的
// 在 CI 上跑一次（要有 Ollama、要拉模型、要好幾分鐘 CPU 推論）才會被執行，
// 判讀邏輯寫錯時沒有任何守門會紅——而它印出來的那句話，正是讀者唯一會看到的
// 結論。抽出來之後 tests/test_eval_summary.py 就能拿真實的 output.json 餵它。
//
// 「只探測 daemon 存活」不足以區分「執行期錯誤」與「模型答錯」，這件事原本就
// 寫在 workflow 的註解裡；但原本的第二道防線（output.json 存在且能 parse）
// 一樣擋不住。**實測（2026-09-11、promptfoo 0.121.19，用 tests/fixtures/
// eval_local/fake_ollama.py 起一個對 /api/tags 回 200、對 /api/chat 回 404
// "model not found" 的假 Ollama）**：
//   - promptfoo 正常跑完（exit 100）並寫出完全合法的 output.json；
//   - 三筆結果的 `response.output` 全是空字串；
//   - `stats.errors` 是 **0**，`failureReason` 是 ASSERT；
//   - 三筆都**有** `error` 欄位，但內容是斷言訊息（"Custom function returned
//     false…"）——跟模型真的答錯時長得一模一樣。
// 所以「檔案能 parse」擋不住，「找有 error 欄位的列」也分不出來（兩種狀態都有）。
// 分得出來的訊號只有一個：**沒有任何一筆拿到非空的模型輸出**。
//
// 用法：node summarize_eval.js [output.json]；markdown 印到 stdout。
// 一律以 0 結束——這支程式負責「講清楚發生什麼事」，紅不紅由 workflow 拿
// promptfoo 自己的離開碼決定。
'use strict';

const fs = require('fs');

const OUTPUT_PATH = process.argv[2] || 'output.json';
const MODEL = process.env.MODEL || '未知模型';

// 歷史對照是固定事實，**一律寫死、不要內插本次的數字**：3/3 是 2026-07-15 用
// 3 題考 gpt-4o-mini 的實測，33 個百分點是 1/3 的算術。把本次題數代進這幾句，
// 題數一變就會印出捏造的歷史量測與錯誤的算術。
const BASELINE_QUESTIONS = 3;

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

/** promptfoo 的一列＝一題 ×一個 provider，所以列數不等於題數。 */
function countDistinct(rows, pick) {
  const seen = new Set();
  rows.forEach((row, index) => {
    const key = pick(row);
    seen.add(key === undefined || key === null ? `#${index}` : String(key));
  });
  return seen.size;
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
  const answeredRows = rows.filter(answered);
  const errorCount = Number.isFinite(Number(stats.errors)) ? Number(stats.errors) : 0;
  const questions = countDistinct(rows, (row) => row.testIdx);
  const providers = countDistinct(rows, (row) => {
    const provider = row.provider;
    if (!provider || typeof provider !== 'object') return provider;
    return provider.label || provider.id;
  });

  if (answeredRows.length === 0) {
    lines.push('### ⚠️ eval-local 未完成——執行期錯誤，不是模型品質訊號');
    lines.push('');
    lines.push(`${rows.length} 筆結果**全部沒有拿到模型輸出**（promptfoo 記錄的 errors＝${errorCount}）。`);
    if (errorCount > 0) {
      lines.push('promptfoo 把它們記成 ERROR——多半是打不到服務（連線被拒、中途死亡）。');
    } else {
      lines.push('promptfoo 沒有記成 ERROR，而是把每一筆記成斷言失敗，看起來就像');
      lines.push('「小模型全答錯」——模型沒拉到、載入失敗（OOM）或請求被拒都長這樣。');
    }
    lines.push('');
    lines.push('**不要**把這次的紅當成小模型的品質訊號，請重跑。');
    return lines.join('\n');
  }

  const scored = answeredRows.length;
  const passed = answeredRows.filter((row) => row.success === true).length;
  const unanswered = rows.length - scored;

  lines.push(`### 🏠 eval-local 完成（${MODEL} @ CI runner CPU）`);
  lines.push('');
  if (unanswered > 0) {
    // 沒作答的不能計進分母：那正是本檔要防的誤讀，只是縮小到部分題目。
    lines.push(`- **本次成績：${passed}/${scored}**（另有 ${unanswered} 筆沒拿到模型輸出，不計分）`);
  } else {
    lines.push(`- **本次成績：${passed}/${scored}**`);
  }
  lines.push('- 零 API key、零外部帳號、零費用——模型就跑在 runner 上');
  lines.push('- 這是 **monitor** 不是 gate：紅色是資訊，不擋部署');
  const scope =
    providers > 1
      ? `${questions} 題小樣卷 ×${providers} 個 provider，共 ${rows.length} 筆結果`
      : `${questions} 題小樣卷`;
  lines.push(`- 考的是 golden 題庫的 ${scope}（主線 golden 軌為 6 題）`);
  if (questions === BASELINE_QUESTIONS) {
    lines.push('- 對照組：雲端 gpt-4o-mini 曾以這 3 題拿 3/3（2026-07-15 實測）');
    lines.push('  （但書：3/3 那次跑的是舊版單行斷言，本次跑的是現在的防禦性斷言，');
    lines.push('  兩次的擷取邏輯不同；而且 3 題的樣本小到單題翻面就是 33 個百分點。');
    lines.push('  這個對照足以說明「同一份 golden 可以換模型重考」，但不是精確的模型能力量測。）');
  } else {
    lines.push(`- 沒有可比的對照組：歷史上的 gpt-4o-mini 3/3 考的是 3 題，本次是 ${questions} 題`);
  }
  if (unanswered > 0) {
    lines.push('');
    lines.push(`> ⚠️ 有 ${unanswered} 筆沒有拿到任何模型輸出（已排除在成績外）。`);
    lines.push('> 那幾筆不是答錯而是沒答到，通常代表這次跑得不乾淨，建議重跑。');
  }
  return lines.join('\n');
}

if (require.main === module) {
  process.stdout.write(`${summarize(OUTPUT_PATH)}\n`);
}

module.exports = { summarize, answered, readResults };
