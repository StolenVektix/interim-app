import { useRef, useState } from "react";

const SWIPE_THRESHOLD = 100;

/** EX-15/EX-17: le swipe déclenche onSwipe(direction) ; la carte n'est retirée par le
 * parent qu'après confirmation serveur (voir StackPage) — jamais de manière optimiste. */
export default function SwipeCard({ offer, onSwipe, disabled }) {
  const [dragX, setDragX] = useState(0);
  const [dragging, setDragging] = useState(false);
  const startX = useRef(0);

  function handlePointerDown(e) {
    if (disabled) return;
    setDragging(true);
    startX.current = e.clientX;
    e.currentTarget.setPointerCapture(e.pointerId);
  }

  function handlePointerMove(e) {
    if (!dragging) return;
    setDragX(e.clientX - startX.current);
  }

  function handlePointerUp() {
    if (!dragging) return;
    setDragging(false);
    const distance = dragX;
    setDragX(0);
    if (distance > SWIPE_THRESHOLD) {
      onSwipe("right");
    } else if (distance < -SWIPE_THRESHOLD) {
      onSwipe("left");
    }
  }

  const rotation = dragX / 12;

  return (
    <div
      className="swipe-card"
      style={{
        transform: `translateX(${dragX}px) rotate(${rotation}deg)`,
        transition: dragging ? "none" : "transform 0.2s ease",
      }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
    >
      {dragX > 40 && <span className="swipe-hint hint-right">POSTULER</span>}
      {dragX < -40 && <span className="swipe-hint hint-left">PASSER</span>}
      <h2>{offer.title}</h2>
      <p className="offer-city">{offer.city}</p>
      <p className="offer-wage">
        {offer.hourly_wage} €/h · {offer.weekly_hours} h/semaine
      </p>
      <p className="offer-period">
        Du {offer.start_date} au {offer.end_date}
      </p>
      <p className="offer-description">{offer.description}</p>
      <div className="swipe-buttons">
        <button
          type="button"
          className="swipe-btn reject"
          disabled={disabled}
          onClick={() => onSwipe("left")}
          aria-label="Passer cette annonce"
        >
          ✕
        </button>
        <button
          type="button"
          className="swipe-btn accept"
          disabled={disabled}
          onClick={() => onSwipe("right")}
          aria-label="Postuler à cette annonce"
        >
          ✓
        </button>
      </div>
    </div>
  );
}
