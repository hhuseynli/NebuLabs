import { Navigate, Route, Routes } from "react-router-dom";

import { CommunityProvider } from "./context/CommunityContext";
import { useAuth } from "./hooks/useAuth";
import CommunityPage from "./pages/Community";
import CreateCommunityPage from "./pages/CreateCommunity";
import DashboardPage from "./pages/Dashboard";
import HomePage from "./pages/Home";
import LandingPage from "./pages/Landing";
import LoginPage from "./pages/Login";
import PostDetailPage from "./pages/PostDetail";
import ProfilePage from "./pages/Profile";
import SignupPage from "./pages/Signup";

function Guarded({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <CommunityProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/home" element={<Guarded><HomePage /></Guarded>} />
        <Route path="/create-community" element={<Guarded><CreateCommunityPage /></Guarded>} />
        <Route path="/r/:slug" element={<CommunityPage />} />
        <Route path="/r/:slug/post/:id" element={<PostDetailPage />} />
        <Route path="/r/:slug/dashboard" element={<Guarded><DashboardPage /></Guarded>} />
        <Route path="/u/:username" element={<ProfilePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </CommunityProvider>
  );
}
