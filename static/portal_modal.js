/* portal_modal.js — universal popup modal for the Astra portal.
 *
 * Single global namespace `window.Portal.Modal`. Self-contained: no deps,
 * injects its own CSS, theme-aware (reads --surface/--text/--border CSS
 * vars from the host page so dark/light Just Works).
 *
 * Designed to be the core overlay primitive of the portal — staging edit,
 * item edit, employee edit, confirmations, alerts all sit on top of it.
 *
 * Quick API:
 *   const m = Portal.Modal.open({
 *     id: 'staging-edit',                       // optional, auto-gen if missing
 *     title: 'Edit Staging',                    // string | Node
 *     subtitle: '917-25 Cole St, Toronto',      // string | Node
 *     size: 'sm' | 'md' | 'lg' | 'xl' | 'full', // default 'md'
 *     tabs: [                                   // optional
 *       { id: 'general', label: 'General', content: nodeOrFn },
 *     ],
 *     body: nodeOrString,                       // used when tabs not provided
 *     footer: [
 *       { label: 'Cancel', onClick: ({close}) => close() },
 *       { label: 'Save',  kind: 'primary', onClick: ({modal}) => save(modal) },
 *     ],
 *     onClose: () => {},
 *     closeOnBackdrop: true,
 *     closeOnEsc: true,
 *   });
 *   m.close();                  // programmatic close
 *   m.setTitle('…');
 *   m.setSubtitle('…');
 *   m.setFooter([...]);
 *   m.activateTab('payment');
 *   m.busy(true|false);         // shows the saving spinner overlay
 *
 * Toasts:
 *   Portal.Modal.toast('Saved', 'success');   // kind: info|success|warn|error
 */

(function () {
  if (window.Portal && window.Portal.Modal) return;
  window.Portal = window.Portal || {};

  // ---------- one-time CSS injection ----------
  const CSS = `
    :root {
      --pm-surface: var(--surface, #fff);
      --pm-text: var(--text, #0f172a);
      --pm-text-muted: var(--text-muted, #64748b);
      --pm-border: var(--border, #e2e8f0);
      --pm-border-strong: var(--border-strong, #cbd5e1);
      --pm-accent: var(--accent, #2563eb);
      --pm-accent-soft: var(--accent-soft, rgba(37,99,235,.10));
      --pm-accent-fg: var(--accent-fg, #fff);
      --pm-radius: 14px;
      --pm-radius-sm: 8px;
      --pm-shadow: 0 28px 64px -20px rgba(15,23,42,.45),
                   0 12px 28px -10px rgba(15,23,42,.30);
    }
    .pm-stack { position: fixed; inset: 0; z-index: 9000; pointer-events: none; }
    .pm-stack > * { pointer-events: auto; }

    .pm-backdrop {
      position: fixed; inset: 0;
      background: rgba(15,23,42,.55);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      opacity: 0; transition: opacity 160ms ease;
    }
    .pm-backdrop.in { opacity: 1; }

    .pm-modal {
      position: fixed; left: 50%; top: 50%;
      transform: translate(-50%, -48%) scale(.98);
      opacity: 0; transition: transform 200ms ease, opacity 160ms ease;
      background: var(--pm-surface);
      color: var(--pm-text);
      border: 1px solid var(--pm-border);
      border-radius: var(--pm-radius);
      box-shadow: var(--pm-shadow);
      display: flex; flex-direction: column;
      max-height: 92vh;
      width: min(720px, 94vw);
      overflow: hidden;
    }
    .pm-modal.in { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    .pm-modal[data-size="sm"]  { width: min(420px, 94vw); }
    .pm-modal[data-size="md"]  { width: min(720px, 94vw); }
    .pm-modal[data-size="lg"]  { width: min(960px, 96vw); }
    .pm-modal[data-size="xl"]  { width: min(1180px, 96vw); }
    .pm-modal[data-size="full"]{ width: 96vw; height: 92vh; }

    .pm-header {
      display: flex; align-items: flex-start; gap: 12px;
      padding: 18px 22px 14px;
      border-bottom: 1px solid var(--pm-border);
      flex-shrink: 0;
    }
    .pm-header-text { flex: 1; min-width: 0; }
    .pm-title { font-size: 17px; font-weight: 700; margin: 0;
      letter-spacing: -0.01em; line-height: 1.3; }
    .pm-subtitle { font-size: 13px; color: var(--pm-text-muted);
      margin: 4px 0 0; line-height: 1.4; }
    .pm-close {
      flex-shrink: 0;
      width: 32px; height: 32px; border-radius: 8px;
      background: transparent; border: 0; color: var(--pm-text-muted);
      cursor: pointer; font-size: 22px; line-height: 1;
      display: inline-flex; align-items: center; justify-content: center;
      transition: background 140ms ease, color 140ms ease;
    }
    .pm-close:hover { background: var(--pm-border); color: var(--pm-text); }

    .pm-tabs {
      display: flex; gap: 2px; padding: 0 16px;
      border-bottom: 1px solid var(--pm-border);
      overflow-x: auto;
      flex-shrink: 0;
    }
    .pm-tab {
      padding: 10px 14px; font-size: 13px; font-weight: 500;
      background: transparent; color: var(--pm-text-muted);
      border: 0; border-bottom: 2px solid transparent;
      cursor: pointer; white-space: nowrap;
      font-family: inherit; transition: color 140ms ease, border-color 140ms ease;
    }
    .pm-tab:hover { color: var(--pm-text); }
    .pm-tab.on { color: var(--pm-accent); border-bottom-color: var(--pm-accent); font-weight: 600; }

    .pm-mobile-tabs { display: none; padding: 12px 16px 0; }
    .pm-mobile-tabs select {
      width: 100%; padding: 9px 12px; font-size: 14px; font-weight: 500;
      background: var(--pm-surface); color: var(--pm-text);
      border: 1px solid var(--pm-border); border-radius: var(--pm-radius-sm);
      font-family: inherit;
    }

    .pm-body {
      padding: 18px 22px;
      overflow-y: auto;
      flex: 1; min-height: 0;
      /* No scroll-behavior:smooth — wheel/keyboard scrolling stays instant
         (so the scroll-spy reflects the live position). Tab clicks animate
         via the explicit scrollTo({behavior:'smooth'}) in activateTab. */
    }
    .pm-body::-webkit-scrollbar { width: 10px; }
    .pm-body::-webkit-scrollbar-thumb { background: var(--pm-border-strong);
      border-radius: 5px; border: 2px solid var(--pm-surface); }

    /* Single-scroll layout: every pane is stacked in the body and the
       tab bar acts as a scroll-spy. */
    .pm-tab-pane { display: block; padding-bottom: 8px; }
    .pm-tab-pane + .pm-tab-pane { margin-top: 28px; }
    .pm-pane-head {
      font-size: 13px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.07em;
      color: var(--pm-accent);
      margin: 0 0 14px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--pm-accent-soft);
    }

    .pm-footer {
      display: flex; justify-content: flex-end; align-items: center; gap: 8px;
      padding: 14px 22px;
      border-top: 1px solid var(--pm-border);
      flex-shrink: 0;
    }
    .pm-footer-status { flex: 1; font-size: 12px; color: var(--pm-text-muted); }
    .pm-btn {
      padding: 8px 14px; font-size: 13px; font-weight: 500;
      background: var(--pm-surface); color: var(--pm-text);
      border: 1px solid var(--pm-border); border-radius: 8px;
      cursor: pointer; font-family: inherit;
      transition: background 140ms ease, border-color 140ms ease, opacity 140ms ease;
    }
    .pm-btn:hover { background: var(--pm-border); }
    .pm-btn.primary { background: var(--pm-accent); border-color: var(--pm-accent);
      color: var(--pm-accent-fg); }
    .pm-btn.primary:hover { filter: brightness(1.05); }
    .pm-btn.danger { background: #dc2626; border-color: #dc2626; color: #fff; }
    .pm-btn.ghost { background: transparent; border-color: transparent; }
    .pm-btn.ghost:hover { background: var(--pm-border); }
    .pm-btn:disabled { opacity: .55; cursor: not-allowed; }

    .pm-busy {
      position: absolute; inset: 0;
      background: rgba(255,255,255,.55);
      display: none;
      align-items: center; justify-content: center;
      z-index: 10;
    }
    .pm-busy.on { display: flex; }
    .pm-spinner {
      width: 28px; height: 28px;
      border: 3px solid var(--pm-border-strong);
      border-top-color: var(--pm-accent);
      border-radius: 50%;
      animation: pm-spin .8s linear infinite;
    }
    @keyframes pm-spin { to { transform: rotate(360deg); } }

    /* Toasts */
    .pm-toast-stack {
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      display: flex; flex-direction: column-reverse; gap: 8px;
      z-index: 9999; pointer-events: none;
    }
    .pm-toast {
      pointer-events: auto;
      background: var(--pm-text); color: var(--pm-surface);
      padding: 10px 16px; border-radius: 10px;
      font-size: 13px; font-weight: 500;
      box-shadow: 0 10px 30px -10px rgba(0,0,0,.4);
      opacity: 0; transform: translateY(10px);
      transition: opacity 180ms ease, transform 180ms ease;
      max-width: min(420px, 90vw);
    }
    .pm-toast.in { opacity: 1; transform: translateY(0); }
    .pm-toast.kind-success { background: #16a34a; color: #fff; }
    .pm-toast.kind-warn    { background: #d97706; color: #fff; }
    .pm-toast.kind-error   { background: #dc2626; color: #fff; }

    /* Generic form helpers — consumers can opt-in via these classes */
    .pm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 18px; }
    .pm-grid .full { grid-column: 1 / -1; }
    .pm-field { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
    .pm-field label { font-size: 11px; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.05em; color: var(--pm-text-muted); }
    .pm-field input, .pm-field select, .pm-field textarea {
      width: 100%; padding: 8px 10px; font-size: 13px;
      background: var(--pm-surface); color: var(--pm-text);
      border: 1px solid var(--pm-border); border-radius: var(--pm-radius-sm);
      font-family: inherit;
    }
    .pm-field input:focus, .pm-field select:focus, .pm-field textarea:focus {
      outline: none; border-color: var(--pm-accent);
      box-shadow: 0 0 0 3px var(--pm-accent-soft);
    }
    .pm-field textarea { resize: vertical; min-height: 80px; }
    .pm-field .hint { font-size: 11px; color: var(--pm-text-muted); margin-top: 2px; }
    .pm-field .readonly {
      padding: 8px 10px; font-size: 13px;
      background: var(--pm-accent-soft); color: var(--pm-text);
      border-radius: var(--pm-radius-sm); border: 1px dashed var(--pm-border-strong);
      min-height: 34px; display: flex; align-items: center;
    }
    .pm-section { margin: 18px 0 6px; padding-top: 14px;
      border-top: 1px solid var(--pm-border);
      font-size: 11px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.06em; color: var(--pm-text-muted); }
    .pm-section:first-child { margin-top: 0; padding-top: 0; border-top: 0; }

    .pm-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .pm-chip {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 4px 10px; border-radius: 999px;
      background: var(--pm-accent-soft); color: var(--pm-accent);
      font-size: 12px; font-weight: 500;
      border: 1px solid transparent; cursor: pointer;
      font-family: inherit;
    }
    .pm-chip.on { background: var(--pm-accent); color: var(--pm-accent-fg); }
    .pm-chip.muted { background: transparent; border-color: var(--pm-border);
      color: var(--pm-text-muted); }
    .pm-chip-x { opacity: .6; margin-left: 2px; }
    .pm-chip-x:hover { opacity: 1; }

    .pm-people-picker { display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
      padding: 6px; border: 1px solid var(--pm-border); border-radius: var(--pm-radius-sm);
      min-height: 38px; background: var(--pm-surface); }
    .pm-people-picker select {
      flex: 1; min-width: 100px; border: 0; padding: 4px; font-size: 13px;
      background: transparent; color: var(--pm-text); font-family: inherit;
    }
    .pm-people-picker select:focus { outline: none; }

    .pm-row-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
      margin-top: 10px; }
    .pm-pill-btn { font-size: 12px; padding: 5px 10px; border-radius: 999px;
      background: var(--pm-accent-soft); color: var(--pm-accent);
      border: 0; cursor: pointer; font-family: inherit; }
    .pm-pill-btn:hover { filter: brightness(1.06); }
    .pm-pill-btn.muted { background: transparent; color: var(--pm-text-muted);
      border: 1px solid var(--pm-border); }

    /* Mobile */
    @media (max-width: 720px) {
      .pm-modal { width: 100vw; height: 100vh; max-height: 100vh; border-radius: 0;
        top: 0; left: 0; transform: translate(0,0) scale(.99); }
      .pm-modal.in { transform: translate(0,0) scale(1); }
      .pm-tabs { display: none; }
      .pm-mobile-tabs { display: block; }
      .pm-grid { grid-template-columns: 1fr; }
      .pm-header, .pm-body, .pm-footer { padding-left: 16px; padding-right: 16px; }
    }
  `;
  function injectCSS() {
    if (document.getElementById('pm-css')) return;
    const s = document.createElement('style');
    s.id = 'pm-css';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  // ---------- stack / state ----------
  let stackEl = null;
  let toastStackEl = null;
  const open = new Map();          // id → modal instance
  let lastFocusedBeforeOpen = null;

  function ensureStack() {
    injectCSS();
    if (!stackEl) {
      stackEl = document.createElement('div');
      stackEl.className = 'pm-stack';
      document.body.appendChild(stackEl);
      document.addEventListener('keydown', onGlobalKey);
    }
    if (!toastStackEl) {
      toastStackEl = document.createElement('div');
      toastStackEl.className = 'pm-toast-stack';
      document.body.appendChild(toastStackEl);
    }
  }
  function topModalId() {
    if (open.size === 0) return null;
    const ids = Array.from(open.keys());
    return ids[ids.length - 1];
  }
  function onGlobalKey(e) {
    if (e.key === 'Escape') {
      const tid = topModalId();
      if (!tid) return;
      const m = open.get(tid);
      if (m && m._opts.closeOnEsc !== false) m.close();
    }
  }
  function uid() { return 'pm-' + Math.random().toString(36).slice(2, 9); }

  function nodify(x) {
    if (x == null) return null;
    if (x.nodeType) return x;
    if (typeof x === 'string') {
      const wrap = document.createElement('div');
      wrap.innerHTML = x;
      // If single child, return it; else return the wrap.
      return wrap.childNodes.length === 1 ? wrap.firstChild : wrap;
    }
    return null;
  }

  // ---------- modal instance ----------
  function buildHeader(modal, opts) {
    const h = document.createElement('div');
    h.className = 'pm-header';
    const txt = document.createElement('div');
    txt.className = 'pm-header-text';
    const t = document.createElement('h2');
    t.className = 'pm-title';
    if (opts.title != null) {
      const n = nodify(opts.title);
      if (n) t.appendChild(n); else t.textContent = String(opts.title);
    }
    txt.appendChild(t);
    if (opts.subtitle != null) {
      const s = document.createElement('p');
      s.className = 'pm-subtitle';
      const sn = nodify(opts.subtitle);
      if (sn) s.appendChild(sn); else s.textContent = String(opts.subtitle);
      txt.appendChild(s);
    }
    h.appendChild(txt);
    const x = document.createElement('button');
    x.className = 'pm-close';
    x.type = 'button';
    x.setAttribute('aria-label', 'Close');
    x.textContent = '×';
    x.addEventListener('click', () => modal.close());
    h.appendChild(x);
    modal._headerTitleEl = t;
    modal._headerSubEl = txt.querySelector('.pm-subtitle');
    modal._headerEl = h;
    return h;
  }

  function buildFooter(modal, footer) {
    const f = document.createElement('div');
    f.className = 'pm-footer';
    const status = document.createElement('div');
    status.className = 'pm-footer-status';
    f.appendChild(status);
    modal._footerStatusEl = status;
    (footer || []).forEach(b => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pm-btn' + (b.kind ? ' ' + b.kind : '');
      btn.textContent = b.label || '';
      if (b.id) btn.dataset.id = b.id;
      if (b.disabled) btn.disabled = true;
      if (typeof b.onClick === 'function') {
        btn.addEventListener('click', () => b.onClick({
          modal, close: () => modal.close(), button: btn,
        }));
      }
      f.appendChild(btn);
    });
    modal._footerEl = f;
    return f;
  }

  function buildTabs(modal, tabs) {
    const tabBar = document.createElement('div');
    tabBar.className = 'pm-tabs';
    const mobileWrap = document.createElement('div');
    mobileWrap.className = 'pm-mobile-tabs';
    const select = document.createElement('select');
    mobileWrap.appendChild(select);

    tabs.forEach((t, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'pm-tab' + (i === 0 ? ' on' : '');
      b.textContent = t.label;
      b.dataset.tabId = t.id;
      b.addEventListener('click', () => modal.activateTab(t.id));
      tabBar.appendChild(b);

      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = t.label;
      select.appendChild(opt);
    });
    select.addEventListener('change', () => modal.activateTab(select.value));

    modal._tabBar = tabBar;
    modal._tabSelect = select;
    return [tabBar, mobileWrap];
  }

  function buildBody(modal, opts) {
    const body = document.createElement('div');
    body.className = 'pm-body';
    modal._panes = [];
    if (opts.tabs && opts.tabs.length) {
      opts.tabs.forEach((t) => {
        const pane = document.createElement('section');
        pane.className = 'pm-tab-pane';
        pane.dataset.tabId = t.id;
        // Pane title doubles as the in-content anchor for the tab.
        const head = document.createElement('h3');
        head.className = 'pm-pane-head';
        head.textContent = t.label;
        pane.appendChild(head);
        const c = typeof t.content === 'function' ? t.content({ modal }) : t.content;
        const n = nodify(c);
        if (n) pane.appendChild(n);
        body.appendChild(pane);
        modal._panes.push(pane);
      });
    } else if (opts.body != null) {
      const n = nodify(opts.body);
      if (n) body.appendChild(n);
    }
    modal._bodyEl = body;
    return body;
  }

  // Scroll-spy: as the body scrolls, mark the tab whose pane top sits closest
  // to (but not below) the body's content origin. While a programmatic scroll
  // is in flight we ignore the scroll handler to prevent intermediate flicker.
  // A bottom spacer ensures every pane (including the last) can scroll to the
  // top — without it short tail panes get stuck and the spy can't reach them.
  function setupScrollSpy(modal) {
    if (!modal._panes || !modal._panes.length) return;
    const body = modal._bodyEl;
    if (!body) return;
    modal._scrollLockUntil = 0;

    const spacer = document.createElement('div');
    spacer.className = 'pm-bottom-spacer';
    spacer.setAttribute('aria-hidden', 'true');
    body.appendChild(spacer);
    function sizeSpacer() {
      const last = modal._panes[modal._panes.length - 1];
      if (!last) return;
      const need = Math.max(0, body.clientHeight - last.offsetHeight - 24);
      spacer.style.height = need + 'px';
    }
    modal._sizeSpacer = sizeSpacer;
    window.addEventListener('resize', sizeSpacer);

    const headroom = 40; // px below body top that still counts as "above origin"
    function update() {
      if (Date.now() < modal._scrollLockUntil) return;
      const bodyTop = body.getBoundingClientRect().top;
      let activeId = modal._panes[0].dataset.tabId;
      for (const pane of modal._panes) {
        const top = pane.getBoundingClientRect().top - bodyTop;
        if (top - headroom <= 0) activeId = pane.dataset.tabId;
        else break;
      }
      reflectActiveTab(modal, activeId);
    }
    body.addEventListener('scroll', update, { passive: true });
    // Defer two frames so layout has settled before measuring.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      sizeSpacer();
      update();
    }));
    modal._scrollSpyUpdate = update;
  }

  function reflectActiveTab(modal, tabId) {
    const tabs = modal._tabBar ? Array.from(modal._tabBar.querySelectorAll('.pm-tab')) : [];
    let changed = false;
    tabs.forEach(b => {
      const want = b.dataset.tabId === tabId;
      if (b.classList.contains('on') !== want) { changed = true; b.classList.toggle('on', want); }
    });
    if (modal._tabSelect && modal._tabSelect.value !== tabId) {
      modal._tabSelect.value = tabId;
      changed = true;
    }
    if (changed && typeof modal._opts.onTabChange === 'function') {
      modal._opts.onTabChange(tabId);
    }
  }

  function focusableInside(root) {
    return Array.from(root.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]),'
      + ' select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(el => el.offsetWidth > 0 && el.offsetHeight > 0);
  }

  function makeModal(opts) {
    ensureStack();
    const id = opts.id || uid();
    if (open.has(id)) {
      // reopen — close existing first
      open.get(id).close();
    }
    lastFocusedBeforeOpen = document.activeElement;

    // backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'pm-backdrop';
    if (opts.closeOnBackdrop !== false) {
      backdrop.addEventListener('click', () => modal.close());
    }
    stackEl.appendChild(backdrop);

    const root = document.createElement('div');
    root.className = 'pm-modal';
    root.dataset.size = opts.size || 'md';
    root.dataset.modalId = id;
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.style.position = 'fixed';

    const modal = {
      id,
      el: root,
      _opts: opts,
      _backdrop: backdrop,
      close() {
        try { if (typeof opts.onClose === 'function') opts.onClose(); } catch (e) {}
        if (this._sizeSpacer) {
          window.removeEventListener('resize', this._sizeSpacer);
          this._sizeSpacer = null;
        }
        root.classList.remove('in');
        backdrop.classList.remove('in');
        setTimeout(() => {
          if (root.parentNode) root.parentNode.removeChild(root);
          if (backdrop.parentNode) backdrop.parentNode.removeChild(backdrop);
          open.delete(id);
          if (lastFocusedBeforeOpen && document.body.contains(lastFocusedBeforeOpen)) {
            lastFocusedBeforeOpen.focus();
          }
        }, 200);
      },
      setTitle(t) {
        if (!this._headerTitleEl) return;
        this._headerTitleEl.textContent = '';
        const n = nodify(t);
        if (n) this._headerTitleEl.appendChild(n);
        else this._headerTitleEl.textContent = String(t);
      },
      setSubtitle(s) {
        if (!this._headerEl) return;
        let sub = this._headerEl.querySelector('.pm-subtitle');
        if (!sub) {
          sub = document.createElement('p');
          sub.className = 'pm-subtitle';
          this._headerEl.querySelector('.pm-header-text').appendChild(sub);
        }
        sub.textContent = '';
        const n = nodify(s);
        if (n) sub.appendChild(n);
        else sub.textContent = String(s);
      },
      setFooter(footer) {
        if (!this._footerEl || !this._footerEl.parentNode) return;
        const fresh = buildFooter(this, footer);
        this._footerEl.parentNode.replaceChild(fresh, this._footerEl);
      },
      setStatus(text, kind) {
        if (!this._footerStatusEl) return;
        this._footerStatusEl.textContent = text || '';
        this._footerStatusEl.style.color = kind === 'error' ? '#dc2626'
          : kind === 'success' ? '#16a34a' : '';
      },
      activateTab(tabId) {
        // Scroll the body to the pane and immediately mark the tab active.
        // _scrollLockUntil suppresses the scroll handler during the smooth
        // scroll so it doesn't flip back through intermediate panes.
        reflectActiveTab(this, tabId);
        const pane = (this._panes || []).find(p => p.dataset.tabId === tabId);
        if (pane && this._bodyEl) {
          const bodyRect = this._bodyEl.getBoundingClientRect();
          const paneRect = pane.getBoundingClientRect();
          const target = this._bodyEl.scrollTop + (paneRect.top - bodyRect.top) - 6;
          this._scrollLockUntil = Date.now() + 700;
          this._bodyEl.scrollTo({ top: Math.max(0, target), behavior: 'smooth' });
        }
        if (typeof opts.onTabChange === 'function') opts.onTabChange(tabId);
      },
      activeTab() {
        if (!this._tabBar) return null;
        const a = this._tabBar.querySelector('.pm-tab.on');
        return a ? a.dataset.tabId : null;
      },
      busy(on) {
        let b = root.querySelector(':scope > .pm-busy');
        if (!b) {
          b = document.createElement('div');
          b.className = 'pm-busy';
          const sp = document.createElement('div');
          sp.className = 'pm-spinner';
          b.appendChild(sp);
          root.appendChild(b);
        }
        b.classList.toggle('on', !!on);
      },
    };

    // assemble
    root.appendChild(buildHeader(modal, opts));
    if (opts.tabs && opts.tabs.length) {
      const [tabBar, mobile] = buildTabs(modal, opts.tabs);
      root.appendChild(tabBar);
      root.appendChild(mobile);
    }
    root.appendChild(buildBody(modal, opts));
    root.appendChild(buildFooter(modal, opts.footer || []));
    stackEl.appendChild(root);
    open.set(id, modal);

    // focus trap (lightweight — top of stack only)
    root.addEventListener('keydown', e => {
      if (e.key !== 'Tab') return;
      const items = focusableInside(root);
      if (!items.length) return;
      const first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    });

    // animate in
    requestAnimationFrame(() => {
      backdrop.classList.add('in');
      root.classList.add('in');
      // initial focus → first focusable input/button (skip the close button).
      const items = focusableInside(root).filter(e => !e.classList.contains('pm-close'));
      if (items.length) items[0].focus();
      // Hook up scroll-spy after layout settles.
      setupScrollSpy(modal);
    });

    return modal;
  }

  // ---------- toast ----------
  function showToast(message, kind, duration) {
    ensureStack();
    const el = document.createElement('div');
    el.className = 'pm-toast' + (kind ? ' kind-' + kind : '');
    el.textContent = message;
    toastStackEl.appendChild(el);
    requestAnimationFrame(() => el.classList.add('in'));
    const ms = duration || 2600;
    setTimeout(() => {
      el.classList.remove('in');
      setTimeout(() => el.remove(), 200);
    }, ms);
    return el;
  }

  // ---------- form helpers (consumers can use directly) ----------
  // h() — tiny element builder. children: array of (Node|string|null|false).
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const k in attrs) {
        const v = attrs[k];
        if (v == null || v === false) continue;
        if (k === 'class' || k === 'className') el.className = v;
        else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
        else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2).toLowerCase(), v);
        else if (k === 'dataset' && typeof v === 'object') Object.assign(el.dataset, v);
        else if (k === 'html') el.innerHTML = v;
        else el.setAttribute(k, v);
      }
    }
    children.flat().forEach(c => {
      if (c == null || c === false) return;
      el.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
    });
    return el;
  }

  function field(label, input, opts) {
    opts = opts || {};
    const wrap = h('div', { class: 'pm-field' + (opts.full ? ' full' : '') });
    if (label) wrap.appendChild(h('label', null, label));
    wrap.appendChild(input);
    if (opts.hint) wrap.appendChild(h('div', { class: 'hint' }, opts.hint));
    return wrap;
  }

  // ---------- public API ----------
  window.Portal.Modal = {
    open: makeModal,
    close(id) {
      if (id != null) {
        const m = open.get(id);
        if (m) m.close();
      } else {
        const tid = topModalId();
        if (tid) open.get(tid).close();
      }
    },
    closeAll() {
      Array.from(open.values()).forEach(m => m.close());
    },
    toast: showToast,
    h, field,
    _open: open,
  };
})();
