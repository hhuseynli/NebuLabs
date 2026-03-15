-- Kindling schema bootstrap for Supabase/Postgres
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE revival_phase AS ENUM ('spark', 'pull', 'handoff', 'complete');
CREATE TYPE agent_status AS ENUM ('active', 'retiring', 'retired');
CREATE TYPE activity_level AS ENUM ('high', 'medium', 'low');

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  bio TEXT,
  karma INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS communities (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  rules JSONB DEFAULT '[]',
  member_count INT DEFAULT 1,
  revival_phase revival_phase DEFAULT 'spark',
  human_activity_ratio FLOAT DEFAULT 0.0,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS community_members (
  user_id UUID NOT NULL,
  community_id UUID NOT NULL,
  role TEXT DEFAULT 'member',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, community_id)
);

CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY,
  community_id UUID NOT NULL,
  name TEXT NOT NULL,
  backstory TEXT,
  personality_traits TEXT[] DEFAULT '{}',
  opinion_set JSONB DEFAULT '{}',
  expertise_areas TEXT[] DEFAULT '{}',
  activity_level activity_level DEFAULT 'medium',
  status agent_status DEFAULT 'active',
  post_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS posts (
  id UUID PRIMARY KEY,
  community_id UUID NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  flair TEXT,
  author_id UUID,
  agent_id UUID,
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  opendata_citation TEXT,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comments (
  id UUID PRIMARY KEY,
  post_id UUID NOT NULL,
  community_id UUID NOT NULL,
  body TEXT NOT NULL,
  parent_comment_id UUID,
  author_id UUID,
  agent_id UUID,
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS votes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  community_id UUID NOT NULL,
  post_id UUID,
  comment_id UUID,
  value INT CHECK (value IN (-1, 1)),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID NOT NULL,
  phase revival_phase NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
