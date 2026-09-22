import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import SwipeCard from "./SwipeCard";

/** EX-14 à EX-20: pile de cartes, swipe gauche/droite, gestion du 409 OFFER_CLOSED,
 * état vide, et non-disparition silencieuse en cas d'échec (EX-16). */
export default function StackPage() {
  const [stack, setStack] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(null);
  const [appliedOffer, setAppliedOffer] = useState(null);
  const { logout } = useAuth();

  const loadStack = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get("/api/stack");
      setStack(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStack();
  }, [loadStack]);

  const currentOffer = stack[0];

  async function handleSwipe(direction) {
    if (!currentOffer || pending) return;
    setPending(true);
    setError(null);
    try {
      const result = await api.post(`/api/offers/${currentOffer.id}/swipe`, { direction });
      // La carte n'est retirée qu'après confirmation serveur : pas de disparition silencieuse en cas d'échec (EX-16).
      setStack((s) => s.slice(1));
      if (result.result === "applied") {
        setAppliedOffer(result.offer);
      }
    } catch (err) {
      if (err instanceof ApiError && err.code === "OFFER_CLOSED") {
        // EX-18: annonce clôturée entre-temps -> carte retirée, aucune candidature, message explicite.
        setStack((s) => s.slice(1));
        setError("Cette annonce vient d'être clôturée par l'employeur : votre candidature n'a pas été envoyée.");
      } else {
        setError(`L'action n'a pas pu être enregistrée (${err.message}). La carte reste dans la pile, réessayez.`);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="page worker-page">
      <header className="page-header">
        <h1>Mes annonces</h1>
        <div className="header-actions">
          <Link to="/interimaire/filtre">Mon filtre</Link>
          <button type="button" className="secondary" onClick={logout}>
            Se déconnecter
          </button>
        </div>
      </header>

      {error && <p className="form-error">{error}</p>}

      {appliedOffer && (
        <div className="applied-banner">
          <p>
            Candidature envoyée pour <strong>{appliedOffer.title}</strong> !
          </p>
          <button type="button" className="secondary" onClick={() => setAppliedOffer(null)}>
            Fermer
          </button>
        </div>
      )}

      <div className="stack-area">
        {loading && <p>Chargement de la pile...</p>}
        {!loading && currentOffer && <SwipeCard offer={currentOffer} onSwipe={handleSwipe} disabled={pending} />}
        {!loading && !currentOffer && (
          // EX-20: état vide, jamais complété par des annonces hors filtre.
          <div className="empty-state">
            <p>Plus aucune annonce ne correspond à votre filtre actuel.</p>
            <Link to="/interimaire/filtre">Élargir mon filtre</Link>
          </div>
        )}
      </div>
    </div>
  );
}
