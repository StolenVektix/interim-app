import { useState } from "react";

const CITIES = ["Bordeaux", "Paris"];

const emptyForm = {
  title: "",
  description: "",
  hourly_wage: "",
  weekly_hours: "",
  start_date: "",
  end_date: "",
  city: CITIES[0],
};

/**
 * EX-05: les attributs required/min/max ci-dessous sont un confort d'UX, jamais la
 * validation elle-même — le serveur revalide tout (EX-07, EX-08) et cette page ne fait
 * que relayer ses erreurs de champ (fieldErrors).
 */
export default function OfferForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState(emptyForm);
  const [fieldErrors, setFieldErrors] = useState([]);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setFieldErrors([]);
    setSubmitting(true);
    try {
      await onSubmit({
        ...form,
        hourly_wage: Number(form.hourly_wage),
        weekly_hours: Number(form.weekly_hours),
      });
      setForm(emptyForm);
    } catch (err) {
      setError(err.message);
      setFieldErrors(err.fields ?? []);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="offer-form" onSubmit={handleSubmit}>
      {error && <p className="form-error">{error}</p>}
      <label className={fieldErrors.includes("title") ? "invalid" : ""}>
        Titre
        <input value={form.title} onChange={(e) => update("title", e.target.value)} required />
      </label>
      <label className={fieldErrors.includes("description") ? "invalid" : ""}>
        Description
        <textarea value={form.description} onChange={(e) => update("description", e.target.value)} required />
      </label>
      <label className={fieldErrors.includes("hourly_wage") ? "invalid" : ""}>
        Rémunération horaire brute (€)
        <input
          type="number"
          min="0.01"
          step="0.01"
          value={form.hourly_wage}
          onChange={(e) => update("hourly_wage", e.target.value)}
          required
        />
      </label>
      <label className={fieldErrors.includes("weekly_hours") ? "invalid" : ""}>
        Temps de travail hebdomadaire (heures, 1 à 48)
        <input
          type="number"
          min="1"
          max="48"
          value={form.weekly_hours}
          onChange={(e) => update("weekly_hours", e.target.value)}
          required
        />
      </label>
      <label className={fieldErrors.includes("start_date") ? "invalid" : ""}>
        Date de début
        <input type="date" value={form.start_date} onChange={(e) => update("start_date", e.target.value)} required />
      </label>
      <label className={fieldErrors.includes("end_date") ? "invalid" : ""}>
        Date de fin
        <input type="date" value={form.end_date} onChange={(e) => update("end_date", e.target.value)} required />
      </label>
      <label className={fieldErrors.includes("city") ? "invalid" : ""}>
        Ville
        <select value={form.city} onChange={(e) => update("city", e.target.value)}>
          {CITIES.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </label>
      <div className="form-actions">
        <button type="submit" disabled={submitting}>
          Publier l'annonce
        </button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Annuler
          </button>
        )}
      </div>
    </form>
  );
}
