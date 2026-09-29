# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Slow responses

- Severity: critical.
- Duration: latency P95 lớn hơn 3 giây trong 10 phút.
- Kênh thông báo: Slack `#llmops-alerts`.
- SLI/SLO liên quan: `fast_successful_requests`, mục tiêu 99.5% request hoàn thành trong 3 giây.
- Ảnh hưởng tới người dùng: câu trả lời chậm, có thể timeout hoặc bỏ phiên.
- Ba bước kiểm tra đầu tiên: xác định time range/P95 trên dashboard; lấy một `correlation_id` chậm trong log; mở trace cùng ID và so sánh retrieval với generation.
- Mitigation tạm thời: tắt incident/feature gây chậm, giảm concurrency hoặc trả lời fallback ngắn khi cần.
- Owner: `llmops-oncall`.

## Elevated request failures

- Severity: critical.
- Duration: error rate lớn hơn 2% trong 5 phút.
- Kênh thông báo: Slack `#llmops-alerts`.
- SLI/SLO liên quan: error-rate guardrail ≤ 2% và retrieval success ≥ 90%.
- Ảnh hưởng tới người dùng: request trả lỗi thay vì câu trả lời.
- Ba bước kiểm tra đầu tiên: xem breakdown `error_type`; lọc `request_failed` theo time range; mở trace có `tool_success=false` để xác định retrieval hay generation lỗi.
- Mitigation tạm thời: disable incident, retry/backoff retrieval hoặc chuyển sang fallback response.
- Owner: `llmops-oncall`.

## Quality regression

- Severity: warning.
- Duration: quality proxy trung bình dưới 0.75 trong 15 phút.
- Kênh thông báo: Slack `#llmops-alerts`.
- SLI/SLO liên quan: `quality_score_avg_min: 0.75`.
- Ảnh hưởng tới người dùng: câu trả lời vẫn thành công nhưng ít hữu ích hoặc thiếu ngữ cảnh.
- Ba bước kiểm tra đầu tiên: xác định feature bị ảnh hưởng; lọc trace theo feature/prompt version; so sánh retrieval documents, prompt version, token và output.
- Mitigation tạm thời: rollback label `production` về prompt đã xác nhận, rồi kiểm tra corpus/retrieval.
- Owner: `product-llmops`.
