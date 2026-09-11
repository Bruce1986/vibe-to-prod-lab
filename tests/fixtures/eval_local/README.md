# eval-local 結果判讀的守門素材

這兩份都是 **promptfoo 0.121.19 實際跑出來的 output.json 原檔**，不是手寫的。
手寫一份只能證明「判讀程式吃得下我以為的格式」，證明不了 promptfoo 真的會
長這樣——而整個判讀邏輯的前提正是「promptfoo 在模型沒作答時也會照樣
寫出一份漂亮的結果檔」。

| 檔案 | 怎麼產生的 | 為什麼留著 |
| :--- | :--- | :--- |
| `output_provider_error.json` | 起一個假 Ollama：`/api/tags` 回 200（daemon 看起來活著）、`/api/chat` 回 404 `model "qwen2.5:1.5b" not found`，再用 `promptfooconfig.local.yaml` 跑一次 | 證明這種狀況下 promptfoo **正常結束**（exit 100）並寫出合法 JSON，三筆 `response.output` 全是空字串，而 `stats.errors` 是 **0**、`failureReason` 是 ASSERT。「檔案能 parse」與「找 ERROR 列」兩種直覺守門在這裡都會靜靜放行 |
| `output_answered.json` | 同一份 `tests.small.yaml`，provider 換成 repo 自己的 `mock_provider.js`（預錄回應），跑出 3/3 | 綠的那一側：真的有模型輸出時，判讀要說「完成」並報出正確的 3/3。少了這一份，守門只驗得了會不會紅 |

擷取日期 2026-09-11。promptfoo 換版後結構若有變動，`tests/test_eval_summary.py`
會先紅在「這份 fixture 的形狀還成立嗎」那幾條，而不是靜靜地測到空氣。
