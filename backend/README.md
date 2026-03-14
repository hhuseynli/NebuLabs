# Backend Notes

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy env template:
   cp .env.example .env
4. Start API:
   uvicorn main:app --host 127.0.0.1 --port 8000

From the workspace root, you can also use the shortcut:
./run-backend.sh

## Optional Supabase persistence

Runtime modes are controlled by `APP_MODE`:

- `local`: in-memory auth/data only.
- `hybrid`: Supabase-first auth/data with local fallback.
- `supabase`: Supabase required, no local token fallback.

If `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are set, the backend can persist and read from Supabase.

Schema file:
- db/schema.sql
- db/rls_policies.sql

Production setup order in Supabase SQL editor:
1. Apply `db/schema.sql`
2. Apply `db/rls_policies.sql`
3. Set `APP_MODE=supabase` in backend `.env`

## Tests

Run backend tests:
- pytest
