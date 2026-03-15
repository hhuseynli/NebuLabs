-- Cultify incremental migration
-- Date: 2026-03-15
-- Purpose:
-- 1) Add sentiment cache columns to communities
-- 2) Add fundraiser fields to posts
-- 3) Create pledges table for fundraiser support

BEGIN;

-- 1) Communities: sentiment cache
ALTER TABLE IF EXISTS communities
  ADD COLUMN IF NOT EXISTS sentiment_cache JSONB;

ALTER TABLE IF EXISTS communities
  ADD COLUMN IF NOT EXISTS sentiment_updated_at TIMESTAMPTZ;

-- 2) Posts: fundraiser metadata
ALTER TABLE IF EXISTS posts
  ADD COLUMN IF NOT EXISTS agent_type TEXT;

ALTER TABLE IF EXISTS posts
  ADD COLUMN IF NOT EXISTS fundraiser_meta JSONB;

-- 3) Pledges table
CREATE TABLE IF NOT EXISTS pledges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID NOT NULL,
  community_id UUID NOT NULL,
  user_id UUID NOT NULL,
  amount_suggested INT,
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (post_id, user_id)
);

-- Foreign keys (safe to re-run)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'pledges_post_id_fkey'
  ) THEN
    ALTER TABLE pledges
      ADD CONSTRAINT pledges_post_id_fkey
      FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'pledges_community_id_fkey'
  ) THEN
    ALTER TABLE pledges
      ADD CONSTRAINT pledges_community_id_fkey
      FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'pledges_user_id_fkey'
  ) THEN
    ALTER TABLE pledges
      ADD CONSTRAINT pledges_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
  END IF;
END $$;

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_pledges_post_id ON pledges(post_id);
CREATE INDEX IF NOT EXISTS idx_pledges_community_id ON pledges(community_id);
CREATE INDEX IF NOT EXISTS idx_pledges_user_id ON pledges(user_id);

COMMIT;
