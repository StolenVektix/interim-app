import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import LoginPage from "./auth/LoginPage";
import RegisterPage from "./auth/RegisterPage";
import EmployerOffersPage from "./employer/EmployerOffersPage";
import OfferApplicationsPage from "./employer/OfferApplicationsPage";
import FilterPage from "./worker/FilterPage";
import StackPage from "./worker/StackPage";

/** EX-02/EX-03 côté client : redirige au lieu d'afficher un espace qui ne correspond pas au rôle.
 * La garantie réelle reste serveur (401/403) ; ceci n'est qu'une commodité de navigation. */
function RequireRole({ role, children }) {
  const { isAuthenticated, role: currentRole } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (currentRole !== role) {
    return <Navigate to={currentRole === "employeur" ? "/employeur" : "/interimaire"} replace />;
  }
  return children;
}

function HomeRedirect() {
  const { isAuthenticated, role } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={role === "employeur" ? "/employeur" : "/interimaire"} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/employeur"
          element={
            <RequireRole role="employeur">
              <EmployerOffersPage />
            </RequireRole>
          }
        />
        <Route
          path="/employeur/offres/:offerId/candidatures"
          element={
            <RequireRole role="employeur">
              <OfferApplicationsPage />
            </RequireRole>
          }
        />
        <Route
          path="/interimaire"
          element={
            <RequireRole role="interimaire">
              <StackPage />
            </RequireRole>
          }
        />
        <Route
          path="/interimaire/filtre"
          element={
            <RequireRole role="interimaire">
              <FilterPage />
            </RequireRole>
          }
        />
      </Routes>
    </AuthProvider>
  );
}
