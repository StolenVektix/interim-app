import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import OfferForm from "./OfferForm";

/** EX-06 à EX-10: création, clôture et accès restreint au propriétaire (géré côté serveur ;
 * ici on n'affiche que ses propres annonces, retournées par GET /api/offers/mine). */
export default function EmployerOffersPage() {
  const [offers, setOffers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const { logout } = useAuth();

  const loadOffers = useCallback(async () => {
    try {
      const data = await api.get("/api/offers/mine");
      setOffers(data);
    } catch (err) {
      setLoadError(err.message);
    }
  }, []);

  useEffect(() => {
    loadOffers();
  }, [loadOffers]);

  async function handleCreate(payload) {
    await api.post("/api/offers", payload);
    setShowForm(false);
    await loadOffers();
  }

  async function handleClose(offerId) {
    await api.post(`/api/offers/${offerId}/close`);
    await loadOffers();
  }

  return (
    <div className="page employer-page">
      <header className="page-header">
        <h1>Mes annonces</h1>
        <button type="button" className="secondary" onClick={logout}>
          Se déconnecter
        </button>
      </header>

      {loadError && <p className="form-error">{loadError}</p>}

      {showForm ? (
        <OfferForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
      ) : (
        <button type="button" onClick={() => setShowForm(true)}>
          + Nouvelle annonce
        </button>
      )}

      <ul className="offer-list">
        {offers.map((offer) => (
          <li key={offer.id} className={`offer-card status-${offer.status}`}>
            <h2>{offer.title}</h2>
            <p className="offer-description">{offer.description}</p>
            <p className="offer-meta">
              {offer.hourly_wage} €/h · {offer.weekly_hours} h/semaine · {offer.city}
            </p>
            <p className="offer-period">
              Du {offer.start_date} au {offer.end_date}
            </p>
            <p className="status-badge">{offer.status === "open" ? "Ouverte" : "Clôturée"}</p>
            <div className="offer-actions">
              <Link to={`/employeur/offres/${offer.id}/candidatures`}>Voir les candidatures</Link>
              {offer.status === "open" && (
                <button type="button" className="secondary" onClick={() => handleClose(offer.id)}>
                  Clôturer
                </button>
              )}
            </div>
          </li>
        ))}
        {offers.length === 0 && <p className="empty-hint">Aucune annonce publiée pour l'instant.</p>}
      </ul>
    </div>
  );
}
