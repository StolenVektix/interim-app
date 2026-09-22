import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";

/** EX-22: candidatures d'une annonce, visibles côté employeur propriétaire, avec le profil intérimaire. */
export default function OfferApplicationsPage() {
  const { offerId } = useParams();
  const [applications, setApplications] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/api/offers/${offerId}/applications`)
      .then(setApplications)
      .catch((err) => setError(err.message));
  }, [offerId]);

  return (
    <div className="page">
      <Link to="/employeur">&larr; Retour aux annonces</Link>
      <h1>Candidatures</h1>
      {error && <p className="form-error">{error}</p>}
      <ul className="application-list">
        {applications.map((application) => (
          <li key={application.id} className="application-card">
            <p className="applicant-email">{application.worker.email}</p>
            <p className="status-badge">{application.status}</p>
            <p className="applied-at">{new Date(application.created_at).toLocaleString("fr-FR")}</p>
          </li>
        ))}
        {applications.length === 0 && <p className="empty-hint">Aucune candidature reçue pour l'instant.</p>}
      </ul>
    </div>
  );
}
