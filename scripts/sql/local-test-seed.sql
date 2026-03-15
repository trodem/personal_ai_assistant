\set ON_ERROR_STOP on

BEGIN;

INSERT INTO users (id, email, role, status, subscription_plan, billing_exempt, tenant_id)
VALUES
  ('11111111-1111-1111-1111-111111111001', 'alice.user@seed.local', 'user', 'active', 'free', false, 'tenant-a'),
  ('11111111-1111-1111-1111-111111111002', 'bob.admin@seed.local', 'admin', 'active', 'premium', true, 'tenant-a'),
  ('11111111-1111-1111-1111-111111111003', 'carla.author@seed.local', 'author', 'active', 'premium', true, 'tenant-default'),
  ('11111111-1111-1111-1111-111111111004', 'dan.user@seed.local', 'user', 'active', 'premium', false, 'tenant-b')
ON CONFLICT (id) DO NOTHING;

INSERT INTO memories (
  id,
  user_id,
  memory_type,
  created_at,
  updated_at,
  tenant_id,
  deleted_at,
  deleted_by_user_id,
  delete_reason,
  structured_data_schema_version
)
VALUES
  (
    '22222222-2222-2222-2222-222222222001',
    '11111111-1111-1111-1111-111111111001',
    'expense_event',
    '2026-03-01T08:00:00Z',
    '2026-03-01T08:05:00Z',
    'tenant-a',
    NULL,
    NULL,
    NULL,
    1
  ),
  (
    '22222222-2222-2222-2222-222222222002',
    '11111111-1111-1111-1111-111111111001',
    'inventory_event',
    '2026-03-02T09:10:00Z',
    '2026-03-02T09:10:00Z',
    'tenant-a',
    NULL,
    NULL,
    NULL,
    1
  ),
  (
    '22222222-2222-2222-2222-222222222003',
    '11111111-1111-1111-1111-111111111001',
    'loan_event',
    '2026-03-03T10:00:00Z',
    '2026-03-03T10:00:00Z',
    'tenant-a',
    NULL,
    NULL,
    NULL,
    1
  ),
  (
    '22222222-2222-2222-2222-222222222004',
    '11111111-1111-1111-1111-111111111001',
    'note',
    '2026-03-04T11:30:00Z',
    '2026-03-04T11:30:00Z',
    'tenant-a',
    NULL,
    NULL,
    NULL,
    1
  ),
  (
    '22222222-2222-2222-2222-222222222005',
    '11111111-1111-1111-1111-111111111004',
    'document',
    '2026-03-05T14:00:00Z',
    '2026-03-05T14:00:00Z',
    'tenant-b',
    NULL,
    NULL,
    NULL,
    1
  ),
  (
    '22222222-2222-2222-2222-222222222006',
    '11111111-1111-1111-1111-111111111001',
    'expense_event',
    '2026-03-06T16:00:00Z',
    '2026-03-07T09:20:00Z',
    'tenant-a',
    '2026-03-07T09:20:00Z',
    '11111111-1111-1111-1111-111111111002',
    'duplicate import cleanup',
    1
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO memory_versions (
  id,
  memory_id,
  user_id,
  version_number,
  raw_text,
  item,
  location,
  person,
  action,
  quantity,
  amount,
  currency,
  who,
  what,
  "where",
  "when",
  why,
  how,
  metadata,
  created_at,
  tenant_id,
  structured_data_schema_version
)
VALUES
  (
    '33333333-3333-3333-3333-333333333001',
    '22222222-2222-2222-2222-222222222001',
    '11111111-1111-1111-1111-111111111001',
    1,
    'I bought bread for 3 CHF',
    'bread',
    'coop',
    NULL,
    NULL,
    NULL,
    3.00,
    'CHF',
    'alice',
    'bread purchase',
    'coop',
    '2026-03-01T08:00:00Z',
    'weekly grocery',
    'voice',
    '{"confidence":"medium"}'::jsonb,
    '2026-03-01T08:00:00Z',
    'tenant-a',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333002',
    '22222222-2222-2222-2222-222222222001',
    '11111111-1111-1111-1111-111111111001',
    2,
    'I bought bread for 3.20 CHF at Coop',
    'bread',
    'coop',
    NULL,
    NULL,
    NULL,
    3.20,
    'CHF',
    'alice',
    'bread purchase corrected',
    'coop',
    '2026-03-01T08:05:00Z',
    'price correction',
    'manual edit',
    '{"confidence":"high"}'::jsonb,
    '2026-03-01T08:05:00Z',
    'tenant-a',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333003',
    '22222222-2222-2222-2222-222222222002',
    '11111111-1111-1111-1111-111111111001',
    1,
    'I stored 4 boxes of peas in the cellar',
    'peas',
    'cellar',
    NULL,
    'add',
    4,
    NULL,
    NULL,
    'alice',
    'inventory add',
    'cellar',
    '2026-03-02T09:10:00Z',
    NULL,
    'voice',
    '{"unit":"boxes"}'::jsonb,
    '2026-03-02T09:10:00Z',
    'tenant-a',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333004',
    '22222222-2222-2222-2222-222222222003',
    '11111111-1111-1111-1111-111111111001',
    1,
    'I lent 200 CHF to Marco',
    NULL,
    NULL,
    'Marco',
    'lend',
    NULL,
    200.00,
    'CHF',
    'alice',
    'loan transaction',
    NULL,
    '2026-03-03T10:00:00Z',
    'friend support',
    'voice',
    '{"settled":false}'::jsonb,
    '2026-03-03T10:00:00Z',
    'tenant-a',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333005',
    '22222222-2222-2222-2222-222222222004',
    '11111111-1111-1111-1111-111111111001',
    1,
    'Remember to renew car insurance in April',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'alice',
    'personal reminder',
    NULL,
    '2026-03-04T11:30:00Z',
    NULL,
    'text',
    '{"priority":"medium"}'::jsonb,
    '2026-03-04T11:30:00Z',
    'tenant-a',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333006',
    '22222222-2222-2222-2222-222222222005',
    '11111111-1111-1111-1111-111111111004',
    1,
    'Uploaded invoice PDF for bike service',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    150.00,
    'CHF',
    'dan',
    'service invoice',
    'bike shop',
    '2026-03-05T14:00:00Z',
    NULL,
    'upload',
    '{"document_type":"invoice"}'::jsonb,
    '2026-03-05T14:00:00Z',
    'tenant-b',
    1
  ),
  (
    '33333333-3333-3333-3333-333333333007',
    '22222222-2222-2222-2222-222222222006',
    '11111111-1111-1111-1111-111111111001',
    1,
    'I bought water for 1 CHF',
    'water',
    'kiosk',
    NULL,
    NULL,
    NULL,
    1.00,
    'CHF',
    'alice',
    'duplicate purchase',
    'kiosk',
    '2026-03-06T16:00:00Z',
    NULL,
    'voice',
    '{"duplicate_of":"22222222-2222-2222-2222-222222222001"}'::jsonb,
    '2026-03-06T16:00:00Z',
    'tenant-a',
    1
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO attachments (
  id,
  memory_id,
  user_id,
  file_url,
  file_type,
  storage_key,
  status,
  ocr_status,
  ocr_text,
  content_hash,
  error_code,
  created_at,
  tenant_id
)
VALUES
  (
    '44444444-4444-4444-4444-444444444001',
    '22222222-2222-2222-2222-222222222001',
    '11111111-1111-1111-1111-111111111001',
    'https://seed.local/storage/receipts/a1.jpg',
    'image/jpeg',
    'receipts/tenant-a/a1.jpg',
    'persisted',
    'completed',
    'BREAD 3.20 CHF',
    'hash-seed-a1',
    NULL,
    '2026-03-01T08:06:00Z',
    'tenant-a'
  ),
  (
    '44444444-4444-4444-4444-444444444002',
    '22222222-2222-2222-2222-222222222005',
    '11111111-1111-1111-1111-111111111004',
    'https://seed.local/storage/receipts/b1.png',
    'image/png',
    'receipts/tenant-b/b1.png',
    'proposal_ready',
    'completed',
    'BIKE SERVICE 150 CHF',
    'hash-seed-b1',
    NULL,
    '2026-03-05T14:05:00Z',
    'tenant-b'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO qa_interactions (
  id,
  user_id,
  question_text,
  answer_text,
  confidence,
  source_memory_ids,
  created_at,
  tenant_id
)
VALUES
  (
    '55555555-5555-5555-5555-555555555001',
    '11111111-1111-1111-1111-111111111001',
    'How much did I spend on bread?',
    'You spent 3.20 CHF on bread.',
    'high',
    '["22222222-2222-2222-2222-222222222001"]'::jsonb,
    '2026-03-08T08:00:00Z',
    'tenant-a'
  ),
  (
    '55555555-5555-5555-5555-555555555002',
    '11111111-1111-1111-1111-111111111004',
    'What documents did I upload?',
    'You uploaded one invoice document for bike service.',
    'medium',
    '["22222222-2222-2222-2222-222222222005"]'::jsonb,
    '2026-03-08T09:00:00Z',
    'tenant-b'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO memory_audit_log (
  id,
  tenant_id,
  memory_id,
  actor_user_id,
  action,
  previous_version_id,
  new_version_id,
  details,
  created_at
)
VALUES
  (
    '66666666-6666-6666-6666-666666666001',
    'tenant-a',
    '22222222-2222-2222-2222-222222222001',
    '11111111-1111-1111-1111-111111111001',
    'update',
    '33333333-3333-3333-3333-333333333001',
    '33333333-3333-3333-3333-333333333002',
    '{"reason":"price correction"}'::jsonb,
    '2026-03-01T08:05:00Z'
  ),
  (
    '66666666-6666-6666-6666-666666666002',
    'tenant-a',
    '22222222-2222-2222-2222-222222222006',
    '11111111-1111-1111-1111-111111111002',
    'delete',
    '33333333-3333-3333-3333-333333333007',
    NULL,
    '{"reason":"duplicate import cleanup"}'::jsonb,
    '2026-03-07T09:20:00Z'
  )
ON CONFLICT (id) DO NOTHING;

COMMIT;
