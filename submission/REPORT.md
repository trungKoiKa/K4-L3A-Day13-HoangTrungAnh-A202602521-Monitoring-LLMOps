# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Hoàng Trung Anh
- **MSSV:** A202602521
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/trungKoiKa/K4-L3A-Day13-HoangTrungAnh-A202602521-Monitoring-LLMOps
- **Commit SHA cuối:** Cập nhật SHA của commit nộp bài ngay trước khi push/LMS submission.
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (challenge file giữ cục bộ, không commit).
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-A202602521`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Baseline log validator | `evidence/00-baseline-log-validator.txt` |
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.txt` |
| Structured log | `evidence/04-structured-log.txt` |
| PII redaction | `evidence/05-pii-redaction.txt` |
| Trace list | `evidence/06-trace-list.txt` |
| Trace waterfall | `evidence/07-trace-waterfall.txt` |
| Trace metadata | `evidence/08-trace-metadata.txt` |
| Prompt versions | `evidence/09-prompt-versions.txt` |
| Prompt rollback | `evidence/10-prompt-rollback.txt` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` (source: `evidence/11-dashboard-overview.html`) |
| Practice incident metric | `evidence/12a-practice-incident-metric.txt` |
| Practice incident log | `evidence/13a-practice-incident-log.txt` |
| Practice incident trace | `evidence/14a-practice-incident-trace.txt` |
| Challenge metric | `evidence/12-incident-metric.txt` |
| Challenge log | `evidence/13-incident-log.txt` |
| Challenge trace | `evidence/14-incident-trace.txt` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 (42 record; 40 record thiếu required/context, 0 correlation ID) | 100/100 (89 record, 0 thiếu field, 48 correlation ID, 0 PII) | Baseline output tại `evidence/00-baseline-log-validator.txt`; kết quả cuối tại `evidence/02-log-validator.txt`. |
| `validate_dashboard.py` | 6/6 contract | 6/6 contract | Validator chỉ xác nhận cấu trúc contract; dashboard runtime được kiểm tra riêng bằng `evidence/11-dashboard-overview.png`. |
| `pytest` | 22 passed | 23 passed | Bổ sung test cho correlation headers, request context và PII runtime. |
| Số traces hợp lệ | Chưa có prompt managed | 13+ trace tự tạo, gồm workload và 2 trace prompt evidence | Trace thuộc project Langfuse cá nhân. |
| Số PII leak | 0 | 0 | Xác nhận bằng validator trên log sạch. |
| Latency P95 / TTFT P95 | Baseline trước sửa không đủ correlation/log enrichment để đối chiếu đáng tin cậy | 1646 ms / 50 ms (normal workload) | Official challenge run: P95 3928 ms, median 2654 ms, TTFT 50 ms; retrieval span 2.501 s. |
| Retrieval success rate | Chưa có baseline observability hợp lệ | 100% | `tool_success` được ghi trên event phản hồi. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ, nhận `x-request-id` hoặc sinh `req-<8-hex>`, bind vào structlog, lưu tại `request.state`, và trả lại qua header `x-request-id`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, latency, TTFT, token, cost, quality và trạng thái retrieval.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` duyệt đệ quy mọi string trong event trước JSON renderer/file writer; email, số điện thoại Việt Nam, CCCD và thẻ được thay bằng token `[REDACTED_*]`.
- **Cách kiểm chứng kết quả:** Xem `evidence/02-log-validator.txt`, `evidence/04-structured-log.txt` và `evidence/05-pii-redaction.txt`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Dùng Langfuse CLI với key của project cá nhân; danh sách trace ID nằm trong `evidence/06-trace-list.txt`.
- **Cấu trúc root/retrieval/generation observations:** `handle-chat-request` (AGENT) chứa hai child cùng cấp: `retrieve-context` (RETRIEVER) và `generate-response` (GENERATION).
- **Cách nối trace với log:** Cùng `correlation_id` được ghi trong trace metadata và structured log; ví dụ prompt baseline dùng `req-prompt-baseline`.
- **Prompt name:** `day13-chat`.
- **Version/label baseline:** Version 1 với labels `baseline`, `production`.
- **Version/label candidate:** Version 2 với label `candidate`.
- **Trace ID của mỗi version:** v1 `dce1b68382e987937fb94a59f9c7210f`; v2 `9c28824630ab3d194f371ad46f88f9e1`.
- **Cách promote và rollback `production`:** Đã chuyển `production` sang version 2 qua Langfuse CLI, kiểm tra kết quả, rồi gán lại label về version 1. Chi tiết trong `evidence/10-prompt-rollback.txt`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** `scripts/render_dashboard.py` render sáu panel từ `data/logs.jsonl`; artifact runtime là `evidence/11-dashboard-overview.png` và source tự chứa là `evidence/11-dashboard-overview.html`.
- **SLO và lý do chọn:** `fast_successful_requests` đo response thành công trong ≤3 giây, target 99.5%/28 ngày. Ngưỡng theo contract lab; challenge riêng dùng ngưỡng điều tra 2 giây.
- **Cách tính error budget:** 100% - 99.5% = 0.5% request trong cửa sổ 28 ngày được phép không đạt SLI.
- **Ba alert và runbook tương ứng:** `slow-responses`, `elevated-request-failures`, `quality-regression`; có condition, duration, severity, owner, Slack channel và mitigation trong `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (challenge file được giữ cục bộ và loại khỏi Git).
- **Khoảng thời gian điều tra:** 2026-09-29 10:10:41.535–10:10:56.885 UTC.
- **Triệu chứng từ metrics:** Năm request feature `monitoring` đều vượt ngưỡng challenge 2000 ms; latency 2653–3928 ms, P95 nearest-rank 3928 ms, median 2654 ms so với normal-workload reference P95 1646 ms. TTFT đều 50 ms. Xem `evidence/12-incident-metric.txt`.
- **Log line và correlation ID liên quan:** Request/response pair của `k4-l3a-challenge-s01`, correlation ID `req-d27cf2bd`, có latency 2654 ms và retrieval success. Payload/query không được sao chép vào evidence. Xem `evidence/13-incident-log.txt`.
- **Trace ID và span gây ảnh hưởng:** Trace `2cc622b1829300e0030cff27796932aa`; root `handle-chat-request` 2.656 s, child `retrieve-context` (`RETRIEVER`) 2.501 s, child `generate-response` 0.153 s. Generation ghi model, prompt v1, usage, cost và TTFT; trace metadata có cùng correlation ID. Xem `evidence/14-incident-trace.txt`.
- **Root cause:** Challenge bật `rag_slow`; retrieval chiếm phần áp đảo thời gian (2.501/2.656 s trong trace được chọn), trong khi generation chỉ 0.153 s. Metrics, log và trace cùng chỉ tới retrieval. Một request có root latency 3928 ms; trace kiểm chứng span của request đại diện `req-d27cf2bd`, không suy diễn nguyên nhân riêng cho phần chênh lệch ở outlier.
- **Fix action:** Tắt challenge incident ngay sau workload; `/health` xác nhận `rag_slow: false`, `tool_fail: false`, `cost_spike: false`.
- **Preventive measure:** Cảnh báo SLO hiện cấu hình latency P95 >3 s trong 10 phút; challenge dùng ngưỡng điều tra riêng 2 s nên cả năm request vi phạm challenge dù alert SLO 3 s có thể chưa kích hoạt. Điều tra theo metrics → correlation ID trong log → retrieval/generation observations trong trace; cân nhắc thêm cảnh báo/SLI ngưỡng 2 s nếu đó là mục tiêu vận hành mong muốn.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Dùng observation type cụ thể (`AGENT`, `RETRIEVER`, `GENERATION`) thay vì trace phẳng để xác định chính xác bước retrieval hoặc generation gây chậm/lỗi.
- **Một lỗi/blocker đã gặp:** Baseline log thiếu correlation/enrichment do TODO starter; validator chỉ rõ 40 record thiếu field.
- **Cách tìm nguyên nhân và xử lý:** Đối chiếu validator với middleware/main/log processor, sau đó xóa log baseline khỏi file đo và tạo workload mới.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metric khoanh vùng thời gian/triệu chứng; log chọn request qua correlation ID; trace cùng ID chỉ ra observation gây ảnh hưởng.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version cho phép so sánh và rollback không deploy code; token/cost ở generation phục vụ theo dõi chi phí; SLO/alert biến triệu chứng thành hành động vận hành.
- **Điều quan trọng nhất đã học:** Validator là gate kỹ thuật, nhưng evidence runtime và chuỗi điều tra nhất quán mới chứng minh hệ thống observability hoạt động.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Ảnh dashboard runtime đã có; cần chụp thêm UI Langfuse cho trace list/waterfall/metadata và prompt versions/rollback để evidence nhìn thấy tên project cá nhân. CLI evidence text hiện đã lưu ID/metadata và truy vết challenge.

## 9. Checklist trước khi nộp

- [ ] Tạo commit cuối, cập nhật SHA ở Section 1 và nộp lên LMS/Codelabs.
- [x] Evidence hiện có dùng đường dẫn tương đối.
- [x] Hoàn thành incident evidence chính thức; practice evidence được giữ riêng.
- [ ] Bổ sung ảnh chụp UI Langfuse cho trace list, waterfall, metadata và prompt/rollback.
- [x] Trace/prompt dùng project Langfuse cá nhân, không lưu key/secret trong evidence text.
- [x] Repository đã chạy được theo README; test và validators có evidence.
- [x] Không đưa `.env`, API key, PII thô hoặc evidence người khác vào artifact tạo mới.
