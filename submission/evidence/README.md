# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Evidence hiện có:

```text
00-baseline-log-validator.txt
01-pytest.txt
02-log-validator.txt
03-dashboard-validator.txt
04-structured-log.txt
05-pii-redaction.txt
06-trace-list.txt
07-trace-waterfall.txt
08-trace-metadata.txt
09-prompt-versions.txt
10-prompt-rollback.txt
11-dashboard-overview.png
11-dashboard-overview.html
12-incident-metric.txt
13-incident-log.txt
14-incident-trace.txt
12a-practice-incident-metric.txt
13a-practice-incident-log.txt
14a-practice-incident-trace.txt
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

Các file `12`–`14` là output đã lọc của challenge chính thức; `12a`–`14a` là practice riêng, không thay thế challenge. Evidence `04`, `05`, `13`, `13a` lấy từ terminal hoặc `data/logs.jsonl`. Evidence `06`–`10`, `14`, `14a` lấy từ project Langfuse cá nhân `day13-k4-l3a-<MSSV>`; ảnh chụp UI nên cho thấy tên project. Không mở/chụp trang API Keys. Không đưa nội dung challenge JSON hay query gốc vào repository.

Ảnh UI Langfuse cho các mục `06`–`10` chưa được chụp trong môi trường này; các file cùng số hiện là bản xuất text từ Langfuse CLI, không giả dạng screenshot UI.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.
