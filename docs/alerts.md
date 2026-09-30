# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#alerts-llmops`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ quá lâu (>3s) để nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xem P95/P99 tăng từ khi nào.
  2. Lọc `data/logs.jsonl` tìm request bị chậm, lấy `correlation_id`.
  3. Mở Langfuse trace bằng `correlation_id` để xem span nào (retrieval hay generation) bị nghẽn.
- Mitigation tạm thời: Tạm thời rollback prompt nếu prompt quá dài hoặc tắt tính năng RAG nặng nếu do database chậm.
- Owner: `team-platform`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `2m`
- Kênh thông báo: Slack `#alerts-llmops-critical`
- SLI/SLO liên quan: Tỉ lệ lỗi tổng thể
- Điều kiện và thời gian duy trì: `error_rate > 2%` trong 2 phút
- Ảnh hưởng tới người dùng: Người dùng liên tục nhận lỗi 500 thay vì câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard errors để xem `error_type` phổ biến là gì.
  2. Tìm log `request_failed` để đọc `payload.detail`.
  3. Kiểm tra xem service phụ thuộc (LLM API, Vector DB) có đang downtime không.
- Mitigation tạm thời: Chuyển sang fallback model (model rẻ hơn/nhẹ hơn) hoặc trả về thông báo bảo trì thân thiện cho người dùng.
- Owner: `team-platform`

## Alert 3

- Tên: `QualityDegradation`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#alerts-llmops`
- SLI/SLO liên quan: Điểm chất lượng trung bình (Quality Proxy)
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` trong 10 phút
- Ảnh hưởng tới người dùng: Trả lời sai, chất lượng kém, hoặc có PII bị lọt ra.
- Ba bước kiểm tra đầu tiên:
  1. Xem dashboard để xác nhận xu hướng giảm của quality score.
  2. Tìm các log có `quality_score` thấp, kiểm tra `message_preview` và `answer_preview`.
  3. Kiểm tra trace trên Langfuse để xem LLM đang trả lời gì (hoặc có dính PII không).
- Mitigation tạm thời: Rollback lại prompt version trước đó (được gắn nhãn `production`) vì đây thường là do prompt mới không tốt.
- Owner: `team-ai`
