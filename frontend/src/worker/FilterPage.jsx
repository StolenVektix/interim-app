import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

const CITIES = ["Bordeaux", "Paris"];

const defaultForm = {
  cities: [],
  min_hourly_wage: "",
  min_weekly_hours: "",
  max_weekly_hours: "",
  date_from: "",
  date_to: "",
};

/** EX-11: un seul filtre par intérimaire ; PUT /api/filter l'upserte, GET le précharge. */
export default function FilterPage() {
  const [form, setForm] = useState(defaultForm);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/api/filter")
      .then((data) => {
        if (data) {
          setForm({
            cities: data.cities,
            min_hourly_wage: data.min_hourly_wage,
            min_weekly_hours: data.min_weekly_hours,
            max_weekly_hours: data.max_weekly_hours,
            date_from: data.date_from,
            date_to: data.date_to,
          });
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  function toggleCity(city) {
    setForm((f) => ({
      ...f,
      cities: f.cities.includes(city) ? f.cities.filter((c) => c !== city) : [...f.cities, city],
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      await api.put("/api/filter", {
        ...form,
        min_hourly_wage: Number(form.min_hourly_wage),
        min_weekly_hours: Number(form.min_weekly_hours),
        max_weekly_hours: Number(form.max_weekly_hours),
      });
      // EX-13: le serveur recalcule immédiatement la pile ; on y retourne pour la voir à jour.
      navigate("/interimaire");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <Link to="/interimaire">&larr; Retour à la pile</Link>
      <h1>Mon filtre</h1>
      {error && <p className="form-error">{error}</p>}
      <form className="filter-form" onSubmit={handleSubmit}>
        <fieldset>
          <legend>Villes</legend>
          {CITIES.map((city) => (
            <label key={city} className="checkbox-label">
              <input type="checkbox" checked={form.cities.includes(city)} onChange={() => toggleCity(city)} />
              {city}
            </label>
          ))}
        </fieldset>
        <label>
          Rémunération horaire minimale (€)
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.min_hourly_wage}
            onChange={(e) => setForm((f) => ({ ...f, min_hourly_wage: e.target.value }))}
            required
          />
        </label>
        <label>
          Heures hebdomadaires minimum
          <input
            type="number"
            min="1"
            max="48"
            value={form.min_weekly_hours}
            onChange={(e) => setForm((f) => ({ ...f, min_weekly_hours: e.target.value }))}
            required
          />
        </label>
        <label>
          Heures hebdomadaires maximum
          <input
            type="number"
            min="1"
            max="48"
            value={form.max_weekly_hours}
            onChange={(e) => setForm((f) => ({ ...f, max_weekly_hours: e.target.value }))}
            required
          />
        </label>
        <label>
          Disponible à partir du
          <input
            type="date"
            value={form.date_from}
            onChange={(e) => setForm((f) => ({ ...f, date_from: e.target.value }))}
            required
          />
        </label>
        <label>
          Disponible jusqu'au
          <input
            type="date"
            value={form.date_to}
            onChange={(e) => setForm((f) => ({ ...f, date_to: e.target.value }))}
            required
          />
        </label>
        <button type="submit" disabled={form.cities.length === 0}>
          Enregistrer le filtre
        </button>
      </form>
    </div>
  );
}
