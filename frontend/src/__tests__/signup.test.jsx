import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import SignupPage from "../pages/Signup";
import { AuthProvider } from "../context/AuthContext";

function renderSignup() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <SignupPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("SignupPage", () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user: { id: "u1", username: "alice", karma: 0 },
        token: "token-123",
      }),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("submits signup form and stores auth data", async () => {
    const user = userEvent.setup();
    renderSignup();

    await user.type(screen.getByPlaceholderText("Email"), "alice@example.com");
    await user.type(screen.getByPlaceholderText("Username"), "alice");
    await user.type(screen.getByPlaceholderText("Password"), "password123");
    await user.click(screen.getByRole("button", { name: "Sign Up" }));

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem("kindling_token")).toBe("token-123");
    expect(localStorage.getItem("kindling_user")).toContain("alice");
  });
});
