import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { CookbookPage } from "./pages/CookbookPage";
import { CookModePage } from "./pages/CookModePage";
import { IngestPage } from "./pages/IngestPage";
import { LoginPage } from "./pages/LoginPage";
import { RecipeDetailPage } from "./pages/RecipeDetailPage";
import { RegisterPage } from "./pages/RegisterPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/cookbook" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/cookbook"
        element={
          <ProtectedRoute>
            <CookbookPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/recipes/new"
        element={
          <ProtectedRoute>
            <IngestPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/recipes/:id"
        element={
          <ProtectedRoute>
            <RecipeDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/recipes/:id/cook"
        element={
          <ProtectedRoute>
            <CookModePage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
