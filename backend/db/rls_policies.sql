-- Row Level Security policies for Supabase production mode
-- Run after schema.sql and after you confirm users.id maps to auth.users.id.

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase_history ENABLE ROW LEVEL SECURITY;

-- Users: can read/update only their own profile.
CREATE POLICY users_select_self ON users
FOR SELECT
USING (id = auth.uid());

CREATE POLICY users_update_self ON users
FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

-- Community membership table.
CREATE POLICY members_select_own_memberships ON community_members
FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY members_insert_self ON community_members
FOR INSERT
WITH CHECK (user_id = auth.uid());

CREATE POLICY members_delete_self ON community_members
FOR DELETE
USING (user_id = auth.uid());

-- Communities: readable by members; writeable by owner.
CREATE POLICY communities_select_member ON communities
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = communities.id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY communities_insert_owner ON communities
FOR INSERT
WITH CHECK (created_by = auth.uid());

CREATE POLICY communities_update_owner ON communities
FOR UPDATE
USING (created_by = auth.uid())
WITH CHECK (created_by = auth.uid());

-- Agents and posts/comments/history are visible within joined communities.
CREATE POLICY agents_select_member ON agents
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = agents.community_id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY posts_select_member ON posts
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = posts.community_id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY comments_select_member ON comments
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = comments.community_id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY phase_history_select_member ON phase_history
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = phase_history.community_id
      AND cm.user_id = auth.uid()
  )
);

-- Posts/comments: author writes only in communities they joined.
CREATE POLICY posts_insert_member ON posts
FOR INSERT
WITH CHECK (
  author_id = auth.uid()
  AND EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = posts.community_id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY comments_insert_member ON comments
FOR INSERT
WITH CHECK (
  author_id = auth.uid()
  AND EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = comments.community_id
      AND cm.user_id = auth.uid()
  )
);

-- Votes: user can only vote as themselves in joined communities.
CREATE POLICY votes_select_self ON votes
FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY votes_insert_self ON votes
FOR INSERT
WITH CHECK (
  user_id = auth.uid()
  AND EXISTS (
    SELECT 1
    FROM community_members cm
    WHERE cm.community_id = votes.community_id
      AND cm.user_id = auth.uid()
  )
);

CREATE POLICY votes_delete_self ON votes
FOR DELETE
USING (user_id = auth.uid());
