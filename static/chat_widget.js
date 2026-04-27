/**
 * Astra Chat floating widget — always-visible button in bottom-right of
 * every webapp page. Click expands a slide-up panel that hosts the
 * existing /chat page in an iframe (same origin, so it inherits the
 * employee token from localStorage).
 */
(function () {
  if (window.__astraChatWidget) return;
  window.__astraChatWidget = true;

  // Skip when the page already IS /chat — no need to nest.
  if (location.pathname === '/chat' || location.pathname.startsWith('/chat/')) return;

  // Skip on the public marketing site (port 5001) — only run on the
  // operations webapp. We detect by the presence of /signin or /portal
  // path conventions; the marketing site doesn't include this script
  // since it's served by a different FastHTML app.

  const css = `
  .astra-chat-fab {
    position: fixed; z-index: 2147483600;
    width: 56px; height: 56px; border-radius: 50%;
    background: #3b82f6; color: #fff; border: 0; cursor: grab;
    box-shadow: 0 6px 20px rgba(0,0,0,.25);
    display: flex; align-items: center; justify-content: center;
    transition: background .15s ease, left .25s cubic-bezier(.2,.7,.3,1.2),
                right .25s cubic-bezier(.2,.7,.3,1.2),
                top .25s cubic-bezier(.2,.7,.3,1.2);
    font: 600 14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;
    touch-action: none;  /* let us own pointer events on mobile */
    user-select: none;
  }
  .astra-chat-fab:hover { background: #2563eb; }
  .astra-chat-fab.dragging {
    cursor: grabbing;
    transition: none;
    transform: scale(1.06);
  }
  .astra-chat-fab svg { width: 26px; height: 26px; fill: currentColor; pointer-events: none; }
  .astra-chat-fab .badge {
    position: absolute; top: -3px; right: -3px;
    background: #dc2626; color: #fff; font-size: 11px; font-weight: 700;
    min-width: 18px; height: 18px; border-radius: 9px; padding: 0 5px;
    display: none; align-items: center; justify-content: center;
    border: 2px solid #fff;
  }
  .astra-chat-fab .badge.show { display: flex; }
  .astra-chat-panel {
    position: fixed; bottom: 88px; z-index: 2147483601;
    width: 380px; height: min(640px, calc(100vh - 110px));
    background: #fff; border-radius: 14px; overflow: hidden;
    box-shadow: 0 18px 60px rgba(0,0,0,.3);
    display: none; flex-direction: column;
    transform: scale(.95) translateY(8px); opacity: 0;
    transition: transform .18s ease, opacity .18s ease;
  }
  .astra-chat-panel.side-right { right: 20px; transform-origin: bottom right; }
  .astra-chat-panel.side-left  { left: 20px;  transform-origin: bottom left;  }
  .astra-chat-panel.open { display: flex; transform: scale(1) translateY(0); opacity: 1; }
  .astra-chat-panel iframe {
    flex: 1; width: 100%; border: 0; background: #f4f5f7;
  }
  @media (max-width: 480px) {
    .astra-chat-panel {
      right: 0; left: 0; bottom: 0;
      width: 100vw; height: 90vh;
      border-radius: 14px 14px 0 0;
    }
    .astra-chat-fab { right: 14px; bottom: 14px; }
  }
  `;

  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  const btn = document.createElement('button');
  btn.className = 'astra-chat-fab';
  btn.title = 'Chat';
  btn.setAttribute('aria-label', 'Open chat');
  btn.innerHTML = `
    <svg viewBox="0 0 24 24"><path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm-4 11H8a1 1 0 1 1 0-2h8a1 1 0 1 1 0 2zm0-4H8a1 1 0 1 1 0-2h8a1 1 0 1 1 0 2z"/></svg>
    <span class="badge"></span>
  `;
  document.body.appendChild(btn);

  // ---- position (drag anywhere vertically, snap to L/R edge) ----
  const POS_KEY = 'astra_chat_fab_pos';
  function loadPos() {
    try {
      const raw = localStorage.getItem(POS_KEY);
      if (!raw) return { side: 'right', y: 0.85 };
      const obj = JSON.parse(raw);
      return {
        side: obj.side === 'left' ? 'left' : 'right',
        y: typeof obj.y === 'number' ? Math.min(1, Math.max(0, obj.y)) : 0.85,
      };
    } catch (e) {
      return { side: 'right', y: 0.85 };
    }
  }
  function savePos(p) {
    try { localStorage.setItem(POS_KEY, JSON.stringify(p)); } catch (e) {}
  }
  let pos = loadPos();

  const EDGE = 16;     // gap between FAB and screen edge
  const TOP_INSET = 12;
  const BOTTOM_INSET = 12;

  function applyPos() {
    const fabH = btn.offsetHeight || 56;
    const usable = Math.max(0, window.innerHeight - TOP_INSET - BOTTOM_INSET - fabH);
    btn.style.top = (TOP_INSET + usable * pos.y) + 'px';
    if (pos.side === 'right') {
      btn.style.right = EDGE + 'px';
      btn.style.left = '';
    } else {
      btn.style.left = EDGE + 'px';
      btn.style.right = '';
    }
  }
  applyPos();
  window.addEventListener('resize', applyPos);

  // Drag handling. We use pointer events for unified mouse/touch/pen.
  // A tap (no movement past the threshold) opens the panel; a drag moves
  // the FAB and snaps it to whichever edge the center ends up nearer.
  let dragState = null;
  const DRAG_THRESHOLD = 6;

  btn.addEventListener('pointerdown', (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    btn.setPointerCapture(e.pointerId);
    const r = btn.getBoundingClientRect();
    dragState = {
      pointerId: e.pointerId,
      startX: e.clientX,
      startY: e.clientY,
      offsetX: e.clientX - r.left,
      offsetY: e.clientY - r.top,
      moved: false,
    };
  });

  btn.addEventListener('pointermove', (e) => {
    if (!dragState || e.pointerId !== dragState.pointerId) return;
    const dx = e.clientX - dragState.startX;
    const dy = e.clientY - dragState.startY;
    if (!dragState.moved && Math.hypot(dx, dy) > DRAG_THRESHOLD) {
      dragState.moved = true;
      btn.classList.add('dragging');
    }
    if (dragState.moved) {
      // While dragging we override transitions and use absolute coords.
      btn.style.transition = 'none';
      const left = e.clientX - dragState.offsetX;
      const top = e.clientY - dragState.offsetY;
      btn.style.left = left + 'px';
      btn.style.right = '';
      btn.style.top = top + 'px';
      e.preventDefault();
    }
  });

  function endDrag(e) {
    if (!dragState || (e && e.pointerId !== dragState.pointerId)) return;
    const wasDrag = dragState.moved;
    if (wasDrag) {
      btn.classList.remove('dragging');
      btn.style.transition = '';

      // Snap to nearer side based on the FAB's center.
      const r = btn.getBoundingClientRect();
      const centerX = r.left + r.width / 2;
      const newSide = (centerX < window.innerWidth / 2) ? 'left' : 'right';

      const fabH = r.height;
      const usable = Math.max(0, window.innerHeight - TOP_INSET - BOTTOM_INSET - fabH);
      const clampedTop = Math.max(TOP_INSET, Math.min(window.innerHeight - BOTTOM_INSET - fabH, r.top));
      const newY = usable > 0 ? (clampedTop - TOP_INSET) / usable : 0.5;

      pos = { side: newSide, y: Math.max(0, Math.min(1, newY)) };
      savePos(pos);
      // Clear the inline left/top so applyPos can re-anchor cleanly.
      btn.style.left = '';
      btn.style.right = '';
      btn.style.top = '';
      applyPos();
    }
    dragState = null;
    if (wasDrag) {
      // Swallow the click that the browser would otherwise fire after a
      // drag-pointerup on the same element.
      const swallow = (ev) => { ev.stopPropagation(); ev.preventDefault(); };
      btn.addEventListener('click', swallow, { capture: true, once: true });
    }
  }
  btn.addEventListener('pointerup', endDrag);
  btn.addEventListener('pointercancel', endDrag);

  const panel = document.createElement('div');
  panel.className = 'astra-chat-panel';
  panel.innerHTML = '';
  document.body.appendChild(panel);

  let iframe = null;
  let isOpen = false;

  function open() {
    if (!iframe) {
      iframe = document.createElement('iframe');
      iframe.src = '/chat';
      iframe.title = 'Astra Chat';
      panel.appendChild(iframe);
    }
    panel.classList.remove('side-left', 'side-right');
    panel.classList.add('side-' + pos.side);
    panel.classList.add('open');
    isOpen = true;
    badge.classList.remove('show');
    badge.textContent = '';
  }

  function close() {
    panel.classList.remove('open');
    isOpen = false;
  }

  btn.addEventListener('click', () => { isOpen ? close() : open(); });

  // Click outside the panel closes it (but not the FAB itself).
  document.addEventListener('click', (e) => {
    if (!isOpen) return;
    if (panel.contains(e.target) || btn.contains(e.target)) return;
    close();
  });

  // Escape closes.
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) close();
  });

  // Background unread badge: subscribe to SSE in the parent page
  // when the panel is closed. Only kicks in once an employee token
  // exists in localStorage.
  const badge = btn.querySelector('.badge');
  let sse = null;
  let sseRetry = 1000;

  function setBadge(n) {
    if (n > 0) {
      badge.textContent = n > 99 ? '99+' : String(n);
      badge.classList.add('show');
    } else {
      badge.classList.remove('show');
    }
  }

  function refreshUnread() {
    const t = localStorage.getItem('astra_employee_token');
    if (!t) { setBadge(0); return; }
    fetch('/api/v1/chat/conversations', {
      headers: { 'Authorization': 'Bearer ' + t },
    }).then(r => r.ok ? r.json() : null).then(j => {
      if (!j) return;
      const total = (j.conversations || []).reduce((s, c) => s + (c.unread_count || 0), 0);
      setBadge(total);
    }).catch(() => {});
  }

  function connectBgSSE() {
    const t = localStorage.getItem('astra_employee_token');
    if (!t) return;
    if (sse) { try { sse.close(); } catch (e) {} }
    sse = new EventSource('/api/v1/chat/sse?token=' + encodeURIComponent(t));
    sse.addEventListener('hello', () => { sseRetry = 1000; });
    sse.onmessage = () => {
      // Any SSE event might affect unread; re-fetch to keep accurate.
      if (!isOpen) refreshUnread();
    };
    sse.onerror = () => {
      try { sse.close(); } catch (e) {}
      sse = null;
      setTimeout(connectBgSSE, sseRetry);
      sseRetry = Math.min(15000, sseRetry * 2);
    };
  }

  // Initial load: unread + SSE.
  refreshUnread();
  connectBgSSE();

  // Listen for token changes (e.g. /chat iframe sets it after login)
  // so the FAB starts working without a full page reload.
  window.addEventListener('storage', (e) => {
    if (e.key === 'astra_employee_token') {
      if (e.newValue) { connectBgSSE(); refreshUnread(); }
      else { setBadge(0); if (sse) { try { sse.close(); } catch (_) {} sse = null; } }
    }
  });
})();
