const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, { method = "GET", token, body } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.error?.message || "Request failed");
  }

  return data;
}

export const api = {
  signup: (payload) => request("/auth/signup", { method: "POST", body: payload }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload }),
  createCommunity: (token, payload) => request("/communities", { method: "POST", token, body: payload }),
  getCommunity: (slug) => request(`/communities/${slug}`),
  joinCommunity: (token, slug) => request(`/communities/${slug}/join`, { method: "POST", token }),
  leaveCommunity: (token, slug) => request(`/communities/${slug}/leave`, { method: "POST", token }),
  getCommunityPosts: (slug, sort, token) => request(`/communities/${slug}/posts?sort=${sort}`, { token }),
  createPost: (token, slug, payload) => request(`/communities/${slug}/posts`, { method: "POST", token, body: payload }),
  getPost: (postId, token) => request(`/posts/${postId}`, { token }),
  votePost: (token, postId, value) => request(`/posts/${postId}/vote`, { method: "POST", token, body: { value } }),
  getComments: (postId, token) => request(`/posts/${postId}/comments`, { token }),
  createComment: (token, postId, payload) => request(`/posts/${postId}/comments`, { method: "POST", token, body: payload }),
  voteComment: (token, commentId, value) => request(`/comments/${commentId}/vote`, { method: "POST", token, body: { value } }),
  getAgents: (slug) => request(`/communities/${slug}/agents`),
  updateAgent: (token, slug, agentId, status) => request(`/communities/${slug}/agents/${agentId}`, { method: "PATCH", token, body: { status } }),
  getRevival: (slug) => request(`/communities/${slug}/revival`),
  advanceRevival: (token, slug, to_phase) => request(`/communities/${slug}/revival/advance`, { method: "POST", token, body: { to_phase } }),
  getProfile: (username) => request(`/users/${username}`),
  streamUrl: (slug) => `${API_URL}/communities/${slug}/feed/stream`,
};
