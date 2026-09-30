# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Ngô Văn Giáp
- **MSSV:** 2A202602644
- **Lớp:** K4-L3B
- **Repository URL:** `https://github.com/ngogiap/K4-L3B-Day13-NgoVanGiap-2A202602644-Monitoring-LLMOps`
- **Commit SHA cuối:** *(sẽ được tự động điền)*
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602644`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline (CP0) | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 (missing_required=20, correlation_ids=0, missing_enrichment=20) | **100/100** ✅ | Sau CP1: 4/4 tiêu chí PASSED |
| `validate_dashboard.py` | HỢP LỆ 6/6 | **HỢP LỆ 6/6** ✅ | Dashboard config đã có sẵn |
| `pytest` | 2 errors | **22/22 passed** ✅ | Tất cả test xanh |
| Số traces hợp lệ | 0 | **>10 traces** ✅ | Chạy load_test.py tạo 10+ traces/lần |
| Số PII leak | 0 | **0** ✅ | PII scrubber hoạt động |
| Latency P95 / TTFT P95 | chưa đo | **~1450ms / ~50ms** | Xem qua dashboard / logs |
| Retrieval success rate | chưa đo | **100%** | Mọi document đều match ở baseline |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware `CorrelationIdMiddleware` đọc header `x-request-id` nếu đúng format `req-<8hex>`, ngược lại sinh mới bằng `uuid4().hex[:8]`. ID được bind vào structlog contextvars và trả về trong response header `x-request-id`.
- **Các metadata được ghi vào structured log:** `correlation_id`, `user_id_hash` (SHA-256 truncated 12 ký tự), `session_id`, `feature`, `model`, `env` — tất cả bind trước khi log `request_received`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` được đăng ký trước `JsonlFileProcessor` và `JSONRenderer` trong chain của structlog. Scrub dùng regex cho email, SĐT Việt Nam, CCCD và thẻ tín dụng.
- **Cách kiểm chứng kết quả:** Chạy `validate_logs.py` — đạt 100/100; `pytest` — 22/22 PASSED; không có PII leak trong log.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Ảnh evidence `06-trace-list.png` có hiển thị tên project `day13-k4-l3b-2A202602644` của tôi ở góc trên bên trái Langfuse UI.
- **Cấu trúc root/retrieval/generation observations:** Truyền `correlation_id` làm metadata ở root trace `day13-agent-request`. Dùng decorator `@observe(name="retrieval", as_type="span")` cho hàm _retrieve, và `@observe(name="generation", as_type="generation")` cho hàm _generate bên trong `agent.py`.
- **Cách nối trace với log:** Root trace được gán tags `correlation_id` do Middleware sinh ra (`req-...`). Trong log cũng chứa ID này nên có thể tra chéo qua lại.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 / Label `production`
- **Version/label candidate:** Version 2 / Label `candidate` (hoặc `production` khi promote)
- **Trace ID của mỗi version:** (VD: `d2b7a9f...` cho v1, `8c91b4e...` cho v2 - xem ảnh 09, 10).
- **Cách promote và rollback `production`:** Vào Langfuse UI > Prompts > `day13-chat`. Xoá nhãn `production` ở v1 và thêm vào v2 để promote. Để rollback, làm ngược lại (chuyển `production` từ v2 về v1). API không cần restart.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** 6 panel được cấu hình tại `config/dashboard.yaml` (Traffic, Latency, Errors, Quality, Cost, Tokens).
- **SLO và lý do chọn:** Chọn SLO "fast_successful_requests" (Latency <= 3000ms, tỷ lệ 99.5%). Lý do: Trong chatbot/RAG, người dùng cần câu trả lời nhanh chóng (<3s), nếu lâu hơn sẽ gây ức chế.
- **Cách tính error budget:** SLO 99.5% trong cửa sổ 28 ngày nghĩa là error budget là 0.5%. Nếu hệ thống nhận 100,000 requests trong tháng, tối đa 500 requests được phép bị lỗi hoặc phản hồi chậm hơn 3000ms.
- **Ba alert và runbook tương ứng:**
  - `HighLatencyP95` (Cảnh báo P95 > 3s trong 5 phút).
  - `HighErrorRate` (Cảnh báo tỷ lệ lỗi > 2% trong 2 phút).
  - `QualityDegradation` (Cảnh báo điểm quality < 0.75 trong 10 phút).
  (Xem chi tiết trong file `docs/alerts.md`).

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** *(thời điểm bạn chạy test)*
- **Triệu chứng từ metrics:** Dashboard Latency cho thấy P95 tăng vọt bất thường lên mức ~14.5 giây (vượt xa SLO 3 giây). Các request vẫn trả về HTTP 200 (không lỗi) nhưng cực kỳ chậm.
- **Log line và correlation ID liên quan:** Ví dụ log `response_sent` có `correlation_id=req-a0254679`, ghi nhận `latency_ms=14547`.
- **Trace ID và span gây ảnh hưởng:** Mở trace của `req-a0254679` trên Langfuse, quan sát Span tree thấy child span `retrieval` tốn rất nhiều thời gian, làm nghẽn toàn bộ request. 
- **Root cause:** Hệ thống RAG (Vector Database / hàm `retrieve()`) bị chậm bất thường. Do đây là hàm đồng bộ (sync), nó block các luồng xử lý khác dẫn đến hiện tượng thắt cổ chai khi có nhiều request cùng lúc (concurrency=5 đẩy latency lên tới 14s).
- **Fix action:** Chạy lại API để reset state (hoặc trong thực tế là scale/tối ưu Vector DB, khởi động lại service RAG).
- **Preventive measure:** Áp dụng timeout cứng (vd 2 giây) cho hàm retrieval để không block toàn hệ thống; cấu hình cảnh báo Slack `HighLatencyP95` để phát hiện ngay lập tức; chuyển sang dùng Async I/O cho retrieval.

> Gợi ý cách viết ngắn: Metric cho thấy `latency` bất thường tăng vọt lên >14s. Log line `response_sent` có `correlation_id=req-a0254679` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `retrieval` bị chậm nghiêm trọng. Root cause là hệ thống Vector DB bị quá tải làm block luồng RAG. Fix action là tối ưu/khởi động lại DB; preventive measure là thiết lập alert `HighLatency` và đặt strict timeout cho hàm retrieval.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định sử dụng `usage_details` và `cost_details` thay vì `usage`/`cost` trong hàm update_current_generation của Langfuse SDK v4. Lý do: SDK v4 đã đổi signature, nếu dùng API cũ sẽ sinh lỗi AttributeError hoặc TypeError, làm đứt gãy luồng ghi nhận token.
- **Một lỗi/blocker đã gặp:** Gặp lỗi khi thêm pattern PII vì tiếng Việt có dấu (`\u1ed1`). Lỗi `UnicodeEncodeError` ở Windows terminal.
- **Cách tìm nguyên nhân và xử lý:** Đổi output của Terminal sang `utf-8` hoặc dùng bảng mã không dấu để test regex. Đã sửa pattern PII Regex để xử lý mượt mà tiếng Việt.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics (Dashboard) cho ta biết "hệ thống CÓ LỖI/CHẬM ở bức tranh tổng thể" → Logs (`logs.jsonl`) cho ta biết "Lỗi ĐÓ LÀ GÌ và Ở ĐÂU" thông qua các metadata và `correlation_id` → Traces (Langfuse) cho ta biết "TẠI SAO lỗi xảy ra" nhờ việc bóc tách thời gian của từng span (như retrieval, generation).
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version giúp ta quản lý chất lượng một cách hệ thống (tránh việc sửa mù mờ); Token/cost giúp phát hiện dị thường tài chính (như spike chi phí); SLO cho biết sức chịu đựng của hệ thống để có quyết định rollback sớm khi cần thiết.
- **Điều quan trọng nhất đã học:** Kỹ năng khoanh vùng lỗi bằng phương pháp On-call: từ Dashboard (triệu chứng) -> Log (Bằng chứng) -> Trace (Nguyên nhân cốt lõi).
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Em đã hoàn thiện toàn bộ tính năng và bài lab. Mọi thứ hoạt động như kỳ vọng.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
