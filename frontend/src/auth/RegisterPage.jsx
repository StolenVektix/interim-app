import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("interimaire");
  const [error, setError] = useState(null);
  const { register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      const confirmedRole = await register(email, password, role);
      navigate(confirmedRole === "employeur" ? "/employeur" : "/interimaire");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Créer un compte</h1>
        {error && <p className="form-error">{error}</p>}
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Mot de passe
          <input
            type="password"
            value={password}
            minLength={8}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {/* EX-01: le rôle choisi ici est définitif, fixé côté serveur à l'inscription. */}
        <fieldset className="role-choice">
          <legend>Je suis...</legend>
          <label>
            <input
              type="radio"
              name="role"
              value="interimaire"
              checked={role === "interimaire"}
              onChange={() => setRole("interimaire")}
            />
            Intérimaire
          </label>
          <label>
            <input
              type="radio"
              name="role"
              value="employeur"
              checked={role === "employeur"}
              onChange={() => setRole("employeur")}
            />
            Employeur
          </label>
        </fieldset>
        <p className="hint">Ce choix est définitif : il ne pourra plus être modifié ensuite.</p>
        <button type="submit">Créer mon compte</button>
        <p className="auth-switch">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </form>
    </div>
  );
}
