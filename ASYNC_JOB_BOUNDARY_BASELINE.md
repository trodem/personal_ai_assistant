# Asynchronous Job Boundary Baseline (MVP)

## Purpose
Define what runs in HTTP request path versus background worker path.

## Request Path (synchronous)
- `memory_extraction`
- `answer_generation`
- `attachment_ocr_extraction`

## Background Worker (asynchronous)
- `data_export_generation`
- `orphan_attachment_cleanup`
- `account_data_lifecycle_deletion`
- `embedding_generation`

## Boundary Rule
- If completion is required to respond to the current endpoint contract, keep it in `request_path`.
- If work is long-running, retry-oriented, or scheduled maintenance, use `background_worker`.

## Source of Truth (code)
- `backend/app/domain/async_job_boundary.py`
