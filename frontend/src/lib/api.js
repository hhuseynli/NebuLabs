const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";
let unauthorizedHandler = null;

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function setAuthFailureHandler(handler) {
  unauthorizedHandler = typeof handler === "function" ? handler : null;
}

function getValidationMessage(detail) {
  if (!Array.isArray(detail) || detail.length === 0) {
    return null;
  }

  const first = detail[0];
  if (!first || typeof first !== "object") {
    return null;
  }

  const path = Array.isArray(first.loc) ? first.loc.slice(1).join(".") : "field";
  const message = typeof first.msg === "string" ? first.msg : "Invalid input";
  return `${path}: ${message}`;
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
    if (response.status === 401) {
      localStorage.removeItem("kindling_user");
      localStorage.removeItem("kindling_token");
      if (unauthorizedHandler) {
        unauthorizedHandler();
      }
    }

    const validationMessage = getValidationMessage(data.detail);
    throw new Error(validationMessage || data.error?.message || data.detail || "Request failed");
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
  askFAQ: (slug, question) => request(`/communities/${slug}/faq/ask?q=${encodeURIComponent(question)}`),
  getSentiment: (token, slug) => request(`/communities/${slug}/sentiment`, { token }),
  scanFundraiser: (token, slug) => request(`/communities/${slug}/fundraiser/scan`, { method: "POST", token }),
  getPledges: (token, postId) => request(`/posts/${postId}/pledges`, { token }),
  createPledge: (token, postId, payload) => request(`/posts/${postId}/pledge`, { method: "POST", token, body: payload }),
  retractPledge: (token, postId) => request(`/posts/${postId}/pledge`, { method: "DELETE", token }),
  seedDemoScenario: (token, slug, scenario) => request(`/communities/${slug}/demo-seed`, { method: "POST", token, body: { scenario } }),
  getAgents: (slug) => request(`/communities/${slug}/agents`),
  updateAgent: (token, slug, agentId, status) => request(`/communities/${slug}/agents/${agentId}`, { method: "PATCH", token, body: { status } }),
  getRevival: (slug) => request(`/communities/${slug}/revival`),
  advanceRevival: (token, slug, to_phase) => request(`/communities/${slug}/revival/advance`, { method: "POST", token, body: { to_phase } }),
  getProfile: (username) => request(`/users/${username}`),
  streamUrl: (slug) => `${API_URL}/communities/${slug}/feed/stream`,
};
