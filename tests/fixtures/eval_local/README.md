# eval-local 結果判讀的守門素材

這兩份都是 **promptfoo 0.121.19 實際跑出來的 output.json**，不是手寫的。
手寫一份只能證明「判讀程式吃得下我以為的格式」，證明不了 promptfoo 真的會
長這樣——而整個判讀邏輯的前提正是「promptfoo 在模型沒作答時也會照樣
寫出一份漂亮的結果檔」。

| 檔案 | 為什麼留著 |
| :--- | :--- |
| `output_provider_error.json` | 證明「daemon 活著但模型沒作答」時 promptfoo **正常結束**（exit 100）並寫出合法 JSON，三筆 `response.output` 全是空字串，而 `stats.errors` 是 **0**、`failureReason` 是 ASSERT。「檔案能 parse」與「找 ERROR 列」兩種直覺守門在這裡都會靜靜放行 |
| `output_answered.json` | 綠的那一側：真的有模型輸出時，判讀要說「完成」並報出正確的 3/3。少了這一份，守門只驗得了會不會紅 |

擷取日期 2026-09-11。

## 怎麼重新產生

兩份都在 repo 外的暫存目錄跑，跑完再搬進來——**不要在 repo 裡跑**，
promptfoo 會在工作目錄留下 `.promptfoo` 之類的產物。

```bash
# 0) 準備一個暫存工作區（$TMP 自己挑一個暫存路徑）
mkdir -p "$TMP/pfprobe/labs/lab2-golden-eval"
cp -R app fixtures "$TMP/pfprobe/"
cp labs/lab2-golden-eval/{promptfooconfig.local.yaml,tests.small.yaml,mock_provider.js} \
   "$TMP/pfprobe/labs/lab2-golden-eval/"
cd "$TMP/pfprobe" && npm install promptfoo@0.121.19

# 1) output_provider_error.json —— daemon 活著、模型沒作答
python3 <此目錄>/fake_ollama.py &          # /api/tags 回 200、/api/chat 回 404
cd "$TMP/pfprobe/labs/lab2-golden-eval"
npx promptfoo eval -c promptfooconfig.local.yaml --no-progress-bar -o output.json
# → exit 100、output.json 合法、三筆 output 皆空、stats.errors=0

# 2) output_answered.json —— 真的有作答（用 repo 自己的 mock provider 回放）
#    把 promptfooconfig.local.yaml 的 providers 換成 `- id: file://mock_provider.js`
#    （其餘不動，仍讀 tests.small.yaml），再跑一次 → exit 0、3/3
```

搬進本目錄時只做兩件事，其餘一字不改：

1. 改名成 `output_provider_error.json` / `output_answered.json`
   （所以檔案裡內嵌的 `config.outputPath` 仍是當初的 `output.json` /
   `output-healthy.json`、`config.description` 仍是那次 probe 的描述——
   那是原檔的一部分，留著當產生痕跡）。
2. 把 `config.prompts` 裡指向暫存沙箱的絕對路徑換成
   `<擷取當時的暫存沙箱>`——那是某一台機器某一次 session 的路徑，
   留著只會讓人以為它有意義。

promptfoo 換版後結構若有變動，`tests/test_eval_summary.py` 會先紅在
「這份 fixture 的形狀還成立嗎」那兩條，而不是靜靜地測到空氣。
