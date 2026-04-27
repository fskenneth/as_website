"""
/chat — single-page web UI for the internal team chat.

Self-contained: ships its own employee login form (POSTs to
/api/v1/auth/login, stores token in localStorage as
'astra_employee_token'), then drives the rest of the page off the
/api/v1/chat/* endpoints + the SSE stream. Vanilla JS, no build step.
"""
from starlette.responses import HTMLResponse


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Astra Chat</title>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>
  :root {
    --bg: #f4f5f7;
    --panel: #ffffff;
    --border: #e4e7eb;
    --muted: #6b7280;
    --primary: #3b82f6;
    --primary-bg: #eff6ff;
    --bubble-me: #3b82f6;
    --bubble-them: #f1f5f9;
    --bubble-them-text: #0f172a;
    --danger: #dc2626;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); font: 14px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif; color: #111; }
  button { font: inherit; cursor: pointer; }
  input, textarea { font: inherit; }

  #login {
    max-width: 360px; margin: 80px auto; padding: 28px 28px 24px;
    background: var(--panel); border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }
  #login h1 { margin: 0 0 8px; font-size: 20px; }
  #login p { margin: 0 0 18px; color: var(--muted); font-size: 13px; }
  #login label { display: block; font-size: 12px; color: var(--muted); margin: 10px 0 4px; }
  #login input { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; }
  #login button {
    width: 100%; margin-top: 18px; padding: 11px;
    background: var(--primary); color: #fff; border: 0; border-radius: 8px; font-weight: 600;
  }
  #login .err { color: var(--danger); font-size: 12px; margin-top: 10px; min-height: 1em; }

  #app { display: none; height: 100vh; height: 100dvh; }
  #app.show { display: grid; grid-template-columns: 320px 1fr; }

  aside {
    background: var(--panel); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; min-height: 0; position: relative;
  }
  aside header {
    padding: 14px 16px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  aside header .me { font-size: 13px; }
  aside header .me strong { display: block; font-size: 15px; }
  aside header .me span { color: var(--muted); font-size: 12px; }
  aside header button {
    background: transparent; border: 1px solid var(--border); border-radius: 8px;
    padding: 6px 10px; font-size: 12px; color: #111;
  }
  .new-chat-fab {
    position: absolute; right: 18px; bottom: 70px;
    width: 52px; height: 52px; border-radius: 50%;
    background: var(--primary); color: #fff; border: 0; cursor: pointer;
    font-size: 28px; line-height: 1; font-weight: 300;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 18px rgba(0,0,0,.25);
    transition: transform .12s ease, opacity .12s ease;
    z-index: 10;
  }
  .new-chat-fab:hover { transform: translateY(-1px); }
  .new-chat-fab.hidden { opacity: 0; pointer-events: none; transform: scale(0.85); }
  .settings-row {
    border-top: 1px solid var(--border);
    padding: 8px 12px;
  }
  .settings-toggle {
    width: 100%; background: transparent; border: 0; padding: 6px;
    text-align: left; color: var(--muted); font-size: 12px; cursor: pointer;
  }
  .settings-toggle:hover { color: var(--primary); }
  #convs { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
  #convs li {
    padding: 0; border-bottom: 1px solid #f1f5f9; position: relative;
    height: 64px; box-sizing: border-box; overflow: hidden;
    transform: translateY(var(--yield-y, 0px));
    transition: transform .18s cubic-bezier(.2,.7,.3,1);
  }
  #convs li.dragging {
    overflow: visible;
    transform: translateY(var(--drag-y, 0px)) scale(1.02);
    transition: none;
    box-shadow: 0 12px 28px rgba(0,0,0,.22);
    z-index: 5;
  }
  #convs li.dragging .row-fg {
    background: var(--panel);
  }
  #convs li .row-actions-bg {
    position: absolute; top: 0; right: 0; bottom: 0;
    display: flex; align-items: stretch;
  }
  #convs li .row-actions-bg button {
    border: 0; cursor: pointer; width: 84px;
    color: #fff; font-size: 12px; font-weight: 600;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
  }
  #convs li .row-actions-bg .archive-btn { background: #6b7280; }
  #convs li .row-actions-bg .delete-btn { background: var(--danger); }
  #convs li .row-actions-bg svg { width: 20px; height: 20px; }
  #convs li .row-fg {
    position: absolute; inset: 0; padding: 10px 14px;
    background: var(--panel); cursor: pointer;
    display: flex; align-items: center; gap: 12px;
    transition: transform .18s ease;
    user-select: none;
  }
  #convs li:hover .row-fg { background: #f8fafc; }
  #convs li.active .row-fg { background: var(--primary-bg); }
  #convs .avatar {
    width: 36px; height: 36px; border-radius: 50%;
    flex: 0 0 auto; display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 13px; font-weight: 600;
  }
  #convs .body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
  #convs .row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  #convs .title-text { font-weight: 600; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #convs .group-tag {
    font-size: 10px; font-weight: 600; color: var(--muted);
    padding: 1px 5px; border-radius: 4px; background: rgba(0,0,0,.06); flex: 0 0 auto;
  }
  #convs .badge {
    background: var(--primary); color: #fff; font-size: 11px; padding: 1px 7px;
    border-radius: 999px; font-weight: 700; flex: 0 0 auto;
  }
  #convs .preview {
    color: var(--muted); font-size: 12.5px; flex: 1; min-width: 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  #convs .when { color: var(--muted); font-size: 11px; flex: 0 0 auto; }

  main { display: flex; flex-direction: column; min-height: 0; }
  main .empty { margin: auto; color: var(--muted); }
  main header {
    padding: 12px 18px; border-bottom: 1px solid var(--border); background: var(--panel);
  }
  main header h2 { margin: 0; font-size: 16px; }
  main header .members { color: var(--muted); font-size: 12px; margin-top: 2px; }
  #thread {
    flex: 1; overflow-y: auto; padding: 16px 14px; display: flex; flex-direction: column; gap: 0;
  }
  .day-sep {
    text-align: center; color: var(--muted); font-size: 12px; font-weight: 500;
    padding: 14px 0 8px; align-self: center;
  }
  .msg {
    display: grid; grid-template-columns: 36px 1fr; gap: 10px;
    padding: 8px 0; position: relative;
  }
  .msg .av {
    width: 32px; height: 32px; border-radius: 50%; color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
  }
  .msg .head { display: flex; align-items: center; gap: 6px; }
  .msg .head .who { font-size: 14px; font-weight: 600; color: var(--bubble-them-text); }
  .msg .head .when { font-size: 12px; color: var(--muted); }
  .msg .bubble {
    margin-top: 2px; padding: 8px 12px; border-radius: 12px; line-height: 1.45;
    white-space: pre-wrap; word-wrap: break-word; max-width: 90%;
    background: var(--bubble-them); color: var(--bubble-them-text);
    display: inline-block;
  }
  .msg.me .bubble { background: rgba(59,130,246,.12); color: var(--bubble-them-text); }
  .msg.deleted .bubble { font-style: italic; color: var(--muted); background: rgba(0,0,0,.04); }
  .msg .reply-chip {
    border-left: 3px solid rgba(0,0,0,.18); padding: 2px 0 2px 8px;
    margin: 4px 0 6px; font-size: 12.5px; color: var(--muted); max-width: 90%;
  }
  .msg .reply-chip .reply-who { font-weight: 600; color: #4b5563; display: block; }
  .msg .reply-chip .reply-body { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .msg .edited-tag { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .msg .row-actions-msg {
    position: absolute; right: 0; top: 4px; display: none; gap: 4px;
    background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 2px;
    box-shadow: 0 4px 12px rgba(0,0,0,.06);
  }
  .msg:hover .row-actions-msg { display: flex; }
  .msg .row-actions-msg button {
    background: transparent; border: 0; cursor: pointer; padding: 4px 6px;
    border-radius: 4px; font-size: 12px; color: var(--muted);
  }
  .msg .row-actions-msg button:hover { background: rgba(0,0,0,.06); color: var(--primary); }
  .msg .row-actions-msg button.danger:hover { color: var(--danger); }
  .msg .reactions {
    display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;
  }
  .reaction-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(0,0,0,.04);
    border: 1px solid rgba(0,0,0,.1);
    padding: 2px 8px; border-radius: 999px;
    font-size: 12px; cursor: pointer;
    user-select: none;
  }
  .reaction-chip.mine {
    background: rgba(59,130,246,.12);
    border-color: rgba(59,130,246,.45);
    color: var(--primary);
  }
  .reaction-chip:hover { background: rgba(0,0,0,.07); }
  .reaction-chip.mine:hover { background: rgba(59,130,246,.18); }
  .emoji-picker {
    position: absolute; z-index: 60; background: var(--panel);
    border: 1px solid var(--border); border-radius: 12px; padding: 8px;
    box-shadow: 0 12px 28px rgba(0,0,0,.18);
    display: grid; grid-template-columns: repeat(8, 32px); gap: 4px;
  }
  .emoji-picker button {
    background: transparent; border: 0; cursor: pointer;
    width: 32px; height: 32px; font-size: 20px; line-height: 1;
    border-radius: 8px;
  }
  .emoji-picker button:hover { background: rgba(0,0,0,.06); }
  .msg .attachments { display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }
  .msg .att-img {
    max-width: 240px; max-height: 240px; border-radius: 10px; cursor: pointer;
    background: #f1f5f9;
  }
  .msg .att-file {
    display: inline-flex; align-items: center; gap: 8px;
    background: #f1f5f9; border-radius: 10px;
    padding: 8px 12px; font-size: 13px; color: var(--bubble-them-text);
    text-decoration: none;
  }
  .msg .att-file:hover { background: #e2e8f0; }
  #composer .attach-btn {
    background: transparent; color: var(--primary);
    width: 38px; height: 38px; border-radius: 50%; font-size: 18px;
    border: 0; cursor: pointer;
  }
  #composer .attach-btn:hover { background: rgba(59,130,246,.1); }

  #composer {
    border-top: 1px solid var(--border); background: var(--panel);
    padding: 10px 12px; display: flex; gap: 8px; align-items: end;
  }
  #composer textarea {
    flex: 1; border: 1px solid var(--border); border-radius: 18px; resize: none;
    padding: 10px 14px; max-height: 140px; line-height: 1.4;
  }
  #composer button {
    background: var(--primary); color: #fff; border: 0; border-radius: 50%;
    width: 38px; height: 38px; font-size: 18px; line-height: 1;
  }
  #composer button:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Modal */
  .modal-bg {
    position: fixed; inset: 0; background: rgba(15,23,42,.45);
    display: none; align-items: center; justify-content: center; z-index: 50;
  }
  .modal-bg.show { display: flex; }
  .modal {
    background: var(--panel); border-radius: 12px; padding: 22px; width: 90%; max-width: 460px;
    box-shadow: 0 10px 40px rgba(0,0,0,.2);
  }
  .modal h3 { margin: 0 0 12px; font-size: 16px; }
  .modal label { display: block; font-size: 12px; color: var(--muted); margin: 8px 0 4px; }
  .modal input { width: 100%; padding: 9px 11px; border: 1px solid var(--border); border-radius: 8px; }
  .modal .emp-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    max-height: 460px; overflow-y: auto; padding: 4px;
  }
  .emp-card {
    display: flex; flex-direction: column; align-items: center; gap: 8px;
    padding: 14px 8px; border-radius: 12px; cursor: pointer;
    background: #f8fafc; border: 1.5px solid transparent;
    transition: background .12s, border-color .12s;
  }
  .emp-card:hover { background: #eef2ff; }
  .emp-card.selected { background: var(--primary-bg); border-color: var(--primary); }
  .emp-card .av-lg {
    width: 48px; height: 48px; border-radius: 50%; color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 600;
  }
  .emp-card .name { font-size: 13.5px; font-weight: 500; color: #111; }
  .modal .actions { display: flex; gap: 8px; margin-top: 16px; justify-content: flex-end; }
  .modal .actions button {
    border: 1px solid var(--border); background: var(--panel); border-radius: 8px;
    padding: 8px 14px; font-weight: 600;
  }
  .modal .actions button.primary { background: var(--primary); color: #fff; border-color: var(--primary); }

  /* Connection indicator */
  #conn {
    position: fixed; right: 12px; bottom: 12px; padding: 4px 10px;
    background: var(--danger); color: #fff; font-size: 11px; border-radius: 999px;
    display: none; z-index: 60;
  }
  #conn.show { display: block; }

  @media (max-width: 700px) {
    #app.show { grid-template-columns: 1fr; }
    aside { display: none; }
    #app.show.show-thread aside { display: none; }
    #app.show:not(.show-thread) main { display: none; }
    #app.show.show-thread main { display: flex; }
    #app.show:not(.show-thread) aside { display: flex; }
    main header .back { display: inline-block; }
  }
  main header .back { display: none; background: transparent; border: 0; font-size: 16px; color: var(--primary); margin-right: 8px; }
</style>
</head>
<body>

<form id="login" onsubmit="return doLogin(event)">
  <h1>Astra Chat</h1>
  <p>Sign in with your employee account.</p>
  <label>Email</label>
  <input type="email" name="email" required autocomplete="username">
  <label>Password</label>
  <input type="password" name="password" required autocomplete="current-password">
  <button type="submit">Sign in</button>
  <div class="err" id="login-err"></div>
</form>

<div id="app">
  <aside>
    <header>
      <div class="me">
        <strong id="me-name">—</strong>
        <span id="me-role">—</span>
      </div>
      <button onclick="logout()">Sign out</button>
    </header>
    <ul id="convs"></ul>
    <button id="new-chat-fab" class="new-chat-fab" onclick="openNewChat()" aria-label="New Chat">+</button>
    <div class="settings-row">
      <button class="settings-toggle" onclick="toggleEnterToSend()">
        <span id="enter-toggle-label">Enter to send: On</span>
      </button>
    </div>
  </aside>
  <main>
    <div class="empty" id="empty">Select a conversation</div>
    <header style="display:none" id="thread-header">
      <button class="back" onclick="closeThread()">←</button>
      <h2 id="thread-title">—</h2>
      <div class="members" id="thread-members">—</div>
    </header>
    <div id="thread" style="display:none"></div>
    <div id="composer" style="display:none">
      <input type="file" id="att-input" style="display:none"
             accept="image/*,video/*,application/pdf,.doc,.docx,.xls,.xlsx"
             onchange="onAttachmentPicked(event)">
      <button class="attach-btn" id="attach-btn" title="Attach file"
              onclick="document.getElementById('att-input').click()">📎</button>
      <textarea id="composer-input" rows="1" placeholder="Message" onkeydown="onComposerKey(event)" oninput="autoGrow(this)"></textarea>
      <button onclick="sendMessage()" id="send-btn" title="Send">→</button>
    </div>
  </main>
</div>

<div class="modal-bg" id="modal-newchat">
  <div class="modal">
    <div id="new-group-name-row" style="display:none">
      <label>Group name</label>
      <input id="new-group-title" placeholder="">
    </div>
    <div class="emp-grid" id="new-emp-grid"></div>
    <div class="actions">
      <button onclick="closeModal('modal-newchat')">Cancel</button>
      <button class="primary" id="new-confirm-btn" onclick="confirmNewChat()" disabled>Start</button>
    </div>
  </div>
</div>

<div id="conn">Reconnecting…</div>

<script>
const TOKEN_KEY = 'astra_employee_token';
const USER_KEY = 'astra_employee_user';
let token = localStorage.getItem(TOKEN_KEY);
let me = JSON.parse(localStorage.getItem(USER_KEY) || 'null');
let conversations = [];
let activeConvId = null;
let activeMembers = {};
let messageCache = {};
let sse = null;

async function api(path, opts = {}) {
  const headers = Object.assign({ 'Authorization': 'Bearer ' + token }, opts.headers || {});
  if (opts.body && typeof opts.body !== 'string') {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const r = await fetch(path, Object.assign({}, opts, { headers }));
  if (r.status === 401) { logout(); throw new Error('Unauthorized'); }
  if (!r.ok) {
    let msg = 'Error';
    try { msg = (await r.json()).error || msg; } catch (e) {}
    throw new Error(msg);
  }
  return r.json();
}

async function doLogin(ev) {
  ev.preventDefault();
  const f = ev.target;
  const errEl = document.getElementById('login-err');
  errEl.textContent = '';
  try {
    const r = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: f.email.value, password: f.password.value }),
    });
    const j = await r.json();
    if (!r.ok) { errEl.textContent = j.error || 'Sign in failed'; return false; }
    token = j.token; me = j.user;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(me));
    boot();
  } catch (e) {
    errEl.textContent = String(e.message || e);
  }
  return false;
}

function logout() {
  if (sse) { try { sse.close(); } catch (e) {} sse = null; }
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  token = null; me = null;
  document.getElementById('app').classList.remove('show');
  document.getElementById('login').style.display = 'block';
}

async function boot() {
  if (!token || !me) { document.getElementById('login').style.display = 'block'; return; }
  document.getElementById('login').style.display = 'none';
  document.getElementById('app').classList.add('show');
  document.getElementById('me-name').textContent = (me.first_name || '') + ' ' + (me.last_name || '');
  document.getElementById('me-role').textContent = me.user_role || '';
  // Sync the Enter-to-send label with stored preference (default On).
  const ets = localStorage.getItem('astra_enter_to_send') !== '0';
  document.getElementById('enter-toggle-label').textContent =
    'Enter to send: ' + (ets ? 'On' : 'Off');
  await loadConversations();
  connectSSE();
}

async function loadConversations() {
  const j = await api('/api/v1/chat/conversations');
  conversations = j.conversations;
  renderConvList();
}

// Deterministic per-conversation avatar palette (matches iOS + Android).
const CHAT_AVATAR_PALETTE = [
  '#6366f1', '#22a8c7', '#2eaf66', '#f57336',
  '#e84d8c', '#8c5cd9', '#f2b233', '#4d82f2',
];
function avatarColor(c) {
  if (c.channel === 'anna') return '#8c5cd9';
  return CHAT_AVATAR_PALETTE[Math.abs(c.id) % CHAT_AVATAR_PALETTE.length];
}
function initials(s) {
  return (s || '').trim().split(/\\s+/).slice(0, 2)
    .map(p => p[0] || '').join('').toUpperCase();
}

// Per-row swipe state, keyed by conversation id. Lets us preserve the
// drawer-open state across re-renders (e.g. when SSE bumps a preview).
const swipeState = {};
const ACTION_W = 84;        // px width of one action button
const SWIPE_HALF = ACTION_W / 2;

function renderConvList() {
  const ul = document.getElementById('convs');
  ul.innerHTML = '';
  const canDelete = (me && (me.user_role || '').toLowerCase() === 'owner');

  for (const c of conversations) {
    const isAnna = c.channel === 'anna';
    const li = document.createElement('li');
    li.dataset.id = c.id;
    if (c.id === activeConvId) li.classList.add('active');

    // Action drawer (Archive + Delete) pinned behind the foreground.
    if (!isAnna) {
      const bg = document.createElement('div');
      bg.className = 'row-actions-bg';

      const archiveBtn = document.createElement('button');
      archiveBtn.className = 'archive-btn';
      archiveBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.54 5.23l-1.39-1.68C18.88 3.21 18.47 3 18 3H6c-.47 0-.88.21-1.16.55L3.46 5.23C3.17 5.57 3 6.02 3 6.5V19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6.5c0-.48-.17-.93-.46-1.27zM12 17.5L6.5 12H10v-2h4v2h3.5L12 17.5zM5.12 5l.81-1h12l.94 1H5.12z"/></svg>
        Archive`;
      archiveBtn.onclick = (e) => { e.stopPropagation(); resetSwipe(c.id); archiveConv(c.id, true); };
      bg.appendChild(archiveBtn);

      if (canDelete) {
        const delBtn = document.createElement('button');
        delBtn.className = 'delete-btn';
        delBtn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
          Delete`;
        delBtn.onclick = (e) => { e.stopPropagation(); resetSwipe(c.id); deleteConv(c.id); };
        bg.appendChild(delBtn);
      }
      li.appendChild(bg);
    }

    // Foreground (visible card).
    const fg = document.createElement('div');
    fg.className = 'row-fg';

    const av = document.createElement('div');
    av.className = 'avatar';
    av.style.background = avatarColor(c);
    av.textContent = initials(c.title);
    fg.appendChild(av);

    const body = document.createElement('div');
    body.className = 'body';

    const top = document.createElement('div');
    top.className = 'row';
    const ts = document.createElement('span');
    ts.className = 'title-text';
    ts.textContent = c.title;
    top.appendChild(ts);
    if (c.kind === 'group') {
      const tag = document.createElement('span');
      tag.className = 'group-tag';
      tag.textContent = 'Group';
      top.appendChild(tag);
    }
    const when = document.createElement('span');
    when.className = 'when';
    when.textContent = c.last_message_at ? relTime(c.last_message_at) : '';
    top.appendChild(when);

    const bot = document.createElement('div');
    bot.className = 'row';
    const prev = document.createElement('span');
    prev.className = 'preview';
    prev.textContent = c.last_message_preview
      || (c.kind === 'group' ? 'New group' : 'No messages yet');
    bot.appendChild(prev);
    if (c.unread_count > 0) {
      const b = document.createElement('span');
      b.className = 'badge';
      b.textContent = c.unread_count > 99 ? '99+' : c.unread_count;
      bot.appendChild(b);
    }
    body.append(top, bot);
    fg.appendChild(body);

    li.appendChild(fg);

    // Restore swipe state if we had one.
    const swipe = swipeState[c.id];
    if (swipe && swipe.x) fg.style.transform = `translateX(${swipe.x}px)`;

    // Wire up gestures (only for non-Anna rows).
    if (!isAnna) attachRowGestures(li, fg, c, canDelete);
    else fg.onclick = () => openConversation(c.id);

    ul.appendChild(li);
  }
}

function resetSwipe(id) {
  swipeState[id] = { x: 0 };
  const li = document.querySelector(`#convs li[data-id="${id}"]`);
  if (li) {
    const fg = li.querySelector('.row-fg');
    if (fg) fg.style.transform = '';
  }
}

function attachRowGestures(li, fg, c, canDelete) {
  const drawerWidth = canDelete ? ACTION_W * 2 : ACTION_W;
  let startX = 0, startY = 0;
  let baseX = 0;            // current swipe offset when gesture begins
  let mode = null;          // 'swipe' | 'reorder' | null
  let pointerId = null;
  let longPressTimer = null;
  let dragRowEl = null;
  let dragStartIdx = -1;
  let dragOffsetY = 0;

  // Tap → open conversation, unless drawer is open (then close it).
  fg.addEventListener('click', (e) => {
    const cur = swipeState[c.id]?.x || 0;
    if (cur < -2) { resetSwipe(c.id); e.preventDefault(); return; }
    openConversation(c.id);
  });

  fg.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    pointerId = e.pointerId;
    startX = e.clientX; startY = e.clientY;
    baseX = swipeState[c.id]?.x || 0;
    mode = null;
    fg.setPointerCapture(pointerId);

    // Long press → reorder mode.
    longPressTimer = setTimeout(() => {
      if (mode !== null) return;
      mode = 'reorder';
      dragStartIdx = conversations.findIndex(x => x.id === c.id);
      dragRowEl = li;
      dragRowEl.classList.add('dragging');
      // Close any open drawer.
      resetSwipe(c.id); baseX = 0;
      navigator.vibrate?.(30);
    }, 450);
  });

  fg.addEventListener('pointermove', (e) => {
    if (e.pointerId !== pointerId) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    if (mode === null) {
      if (Math.abs(dx) > 6 && Math.abs(dx) > Math.abs(dy)) {
        // Horizontal first → swipe-to-reveal.
        clearTimeout(longPressTimer); longPressTimer = null;
        mode = 'swipe';
      } else if (Math.abs(dy) > 6 && mode !== 'reorder') {
        // Vertical scroll without long-press; let it pass to the list.
        clearTimeout(longPressTimer); longPressTimer = null;
        pointerId = null;
        try { fg.releasePointerCapture(e.pointerId); } catch (_) {}
        return;
      }
    }

    if (mode === 'swipe') {
      const next = Math.max(-drawerWidth, Math.min(0, baseX + dx));
      fg.style.transform = `translateX(${next}px)`;
      e.preventDefault();
    } else if (mode === 'reorder') {
      dragOffsetY = dy;
      dragRowEl.style.setProperty('--drag-y', dy + 'px');
      // Project the target slot from the live drag, then ask the other
      // rows to yield (slide aside) to expose the drop position.
      applyYield(dragStartIdx, dy);
      e.preventDefault();
    }
  });

  fg.addEventListener('pointerup', endRow);
  fg.addEventListener('pointercancel', endRow);
  function endRow(e) {
    if (e.pointerId !== pointerId) return;
    clearTimeout(longPressTimer); longPressTimer = null;
    try { fg.releasePointerCapture(pointerId); } catch (_) {}
    pointerId = null;

    if (mode === 'swipe') {
      const cur = (() => {
        const m = /translateX\(([-\d.]+)px\)/.exec(fg.style.transform || '');
        return m ? parseFloat(m[1]) : 0;
      })();
      const target = (cur <= -SWIPE_HALF) ? -drawerWidth : 0;
      fg.style.transform = `translateX(${target}px)`;
      swipeState[c.id] = { x: target };
    } else if (mode === 'reorder') {
      dragRowEl.classList.remove('dragging');
      dragRowEl.style.removeProperty('--drag-y');
      clearYield();
      const rowH = 64;
      const slots = Math.round(dragOffsetY / rowH);
      const total = conversations.length;
      const annaFirst = total > 0 && conversations[0].channel === 'anna';
      const minIdx = annaFirst ? 1 : 0;
      const target = Math.max(minIdx, Math.min(total - 1, dragStartIdx + slots));
      if (target !== dragStartIdx) {
        const arr = conversations.slice();
        const [item] = arr.splice(dragStartIdx, 1);
        arr.splice(target, 0, item);
        conversations = arr;
        renderConvList();
        const ids = conversations.filter(x => x.channel !== 'anna').map(x => x.id);
        api('/api/v1/chat/conversations/reorder', { method: 'POST', body: { ids } })
          .catch(err => alert('Reorder failed: ' + err.message));
      }
      dragRowEl = null;
    }
    mode = null;
  }
}

/**
 * Apply yield transforms during a reorder drag. As the dragged card moves
 * over a slot, every row in [origin .. target] (or the reverse) shifts a
 * row-height aside so the target gap is visible to the user.
 */
function applyYield(originIdx, dy) {
  const rowH = 64;
  const total = conversations.length;
  const annaFirst = total > 0 && conversations[0].channel === 'anna';
  const minIdx = annaFirst ? 1 : 0;
  const slots = Math.round(dy / rowH);
  const target = Math.max(minIdx, Math.min(total - 1, originIdx + slots));
  const lis = document.querySelectorAll('#convs li');
  lis.forEach((li, i) => {
    if (i === originIdx) return;
    let yieldPx = 0;
    if (target > originIdx && i > originIdx && i <= target) yieldPx = -rowH;
    else if (target < originIdx && i < originIdx && i >= target) yieldPx = rowH;
    li.style.setProperty('--yield-y', yieldPx + 'px');
  });
}

function clearYield() {
  document.querySelectorAll('#convs li').forEach(li => {
    li.style.removeProperty('--yield-y');
  });
}

async function archiveConv(id, archived) {
  const prev = conversations.slice();
  conversations = conversations.filter(c => c.id !== id);
  renderConvList();
  try {
    await api('/api/v1/chat/conversations/' + id + '/archive', {
      method: 'POST', body: { archived },
    });
  } catch (e) {
    conversations = prev; renderConvList();
    alert('Archive failed: ' + e.message);
  }
}

async function deleteConv(id) {
  if (!confirm('Delete this conversation for everyone?')) return;
  const prev = conversations.slice();
  conversations = conversations.filter(c => c.id !== id);
  renderConvList();
  try {
    await api('/api/v1/chat/conversations/' + id, { method: 'DELETE' });
  } catch (e) {
    conversations = prev; renderConvList();
    alert('Delete failed: ' + e.message);
  }
}

async function openConversation(id) {
  activeConvId = id;
  document.querySelectorAll('#convs li').forEach(li => li.classList.toggle('active', +li.dataset.id === id));
  const conv = conversations.find(c => c.id === id);
  document.getElementById('app').classList.add('show-thread');
  document.getElementById('empty').style.display = 'none';
  document.getElementById('thread-header').style.display = 'block';
  document.getElementById('thread').style.display = 'flex';
  document.getElementById('composer').style.display = 'flex';
  document.getElementById('thread-title').textContent = conv ? conv.title : '—';
  // Pull full conversation (members) + messages.
  const detail = await api('/api/v1/chat/conversations/' + id);
  activeMembers = {};
  for (const m of (detail.conversation.members || [])) activeMembers[m.id] = m;
  document.getElementById('thread-members').textContent =
    Object.values(activeMembers).map(m => m.display_name).join(', ');
  const j = await api('/api/v1/chat/conversations/' + id + '/messages?limit=100');
  messageCache[id] = j.messages;
  renderThread();
  document.getElementById('composer-input').focus();
  // Mark read.
  if (j.messages.length) {
    api('/api/v1/chat/conversations/' + id + '/read', {
      method: 'POST', body: { message_id: j.messages[j.messages.length - 1].id },
    }).catch(() => {});
    const c = conversations.find(c => c.id === id);
    if (c) { c.unread_count = 0; renderConvList(); }
  }
}

function closeThread() {
  document.getElementById('app').classList.remove('show-thread');
  activeConvId = null;
}

function dayKey(iso) {
  return (iso || '').slice(0, 10);
}

function dayHeader(iso) {
  if (!iso) return '';
  const d = new Date(iso.replace(' ', 'T') + 'Z');
  const today = new Date();
  const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  const sameDay = (a, b) =>
    a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
  if (sameDay(d, today)) return 'Today';
  if (sameDay(d, yesterday)) return 'Yesterday';
  return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
}

function fmtMessageTime(iso) {
  if (!iso) return '';
  const d = new Date(iso.replace(' ', 'T') + 'Z');
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

function avatarColorForSender(senderId) {
  const palette = ['#6366f1','#22a8c7','#2eaf66','#f57336','#e84d8c','#8c5cd9','#f2b233','#4d82f2'];
  return palette[Math.abs(senderId) % palette.length];
}

function renderThread() {
  const t = document.getElementById('thread');
  t.innerHTML = '';
  const list = messageCache[activeConvId] || [];
  let lastDay = null;
  for (const m of list) {
    const dk = dayKey(m.created_at);
    if (dk !== lastDay) {
      const sep = document.createElement('div');
      sep.className = 'day-sep';
      sep.textContent = dayHeader(m.created_at);
      t.appendChild(sep);
      lastDay = dk;
    }
    appendMessage(m);
  }
  t.scrollTop = t.scrollHeight;
}

function appendMessage(m) {
  const t = document.getElementById('thread');
  const isMine = m.sender_id === me.id;
  const isDeleted = m.deleted || m.deleted_at;

  const div = document.createElement('div');
  div.className = 'msg ' + (isMine ? 'me' : 'them') + (isDeleted ? ' deleted' : '');
  div.dataset.msgId = m.id;

  // Avatar
  const av = document.createElement('div');
  av.className = 'av';
  av.style.background = avatarColorForSender(m.sender_id);
  const senderName = isMine
    ? 'You'
    : (m.sender && m.sender.display_name) || (activeMembers[m.sender_id] && activeMembers[m.sender_id].display_name) || ('User #' + m.sender_id);
  av.textContent = (senderName.split(' ').slice(0, 2).map(p => p[0] || '').join('').toUpperCase()) || '?';
  div.appendChild(av);

  // Right-side: header + reply chip + bubble + edited tag
  const col = document.createElement('div');

  const head = document.createElement('div');
  head.className = 'head';
  const who = document.createElement('span'); who.className = 'who'; who.textContent = senderName;
  const when = document.createElement('span'); when.className = 'when'; when.textContent = fmtMessageTime(m.created_at);
  head.append(who, when);
  col.appendChild(head);

  if (m.reply_to) {
    const chip = document.createElement('div');
    chip.className = 'reply-chip';
    const rw = document.createElement('span'); rw.className = 'reply-who';
    rw.textContent = '« ' + m.reply_to.sender_name;
    const rb = document.createElement('span'); rb.className = 'reply-body';
    rb.textContent = m.reply_to.deleted ? '(message deleted)' : m.reply_to.body;
    chip.append(rw, rb);
    col.appendChild(chip);
  }

  // Attachments — render before the text bubble so empty-body sends look clean.
  if (!isDeleted && Array.isArray(m.attachments) && m.attachments.length > 0) {
    const attsHost = document.createElement('div');
    attsHost.className = 'attachments';
    for (const a of m.attachments) {
      if (a.kind === 'photo') {
        const img = document.createElement('img');
        img.className = 'att-img';
        img.alt = a.original_name || 'photo';
        img.onclick = () => window.open(blobCache[a.url] || a.url, '_blank');
        loadAttachmentImage(img, a.url);
        attsHost.appendChild(img);
      } else {
        const link = document.createElement('a');
        link.className = 'att-file';
        link.href = '#';
        link.textContent = (a.kind === 'video' ? '▶ ' : '📎 ') + (a.original_name || 'File');
        link.onclick = (ev) => {
          ev.preventDefault();
          fetch(a.url, { headers: { 'Authorization': 'Bearer ' + token } })
            .then(r => r.ok ? r.blob() : null)
            .then(blob => {
              if (!blob) return;
              const u = URL.createObjectURL(blob);
              const x = document.createElement('a');
              x.href = u; x.download = a.original_name || 'file';
              document.body.appendChild(x); x.click(); x.remove();
            });
        };
        attsHost.appendChild(link);
      }
    }
    col.appendChild(attsHost);
  }

  // Body text — skip the bubble if the body is just the placeholder "📎"
  // we use server-side when no caption was supplied.
  if (!(isDeleted && false) && (m.body && m.body !== '📎')) {
    const b = document.createElement('div');
    b.className = 'bubble';
    b.textContent = isDeleted ? 'Message deleted' : m.body;
    col.appendChild(b);
  } else if (isDeleted) {
    const b = document.createElement('div');
    b.className = 'bubble';
    b.textContent = 'Message deleted';
    col.appendChild(b);
  }

  if (m.edited_at && !isDeleted) {
    const ed = document.createElement('div'); ed.className = 'edited-tag'; ed.textContent = '(edited)';
    col.appendChild(ed);
  }

  // Reaction chips below the body.
  if (!isDeleted && Array.isArray(m.reactions) && m.reactions.length > 0) {
    const rxnsHost = document.createElement('div');
    rxnsHost.className = 'reactions';
    for (const r of m.reactions) {
      const chip = document.createElement('span');
      const mine = Array.isArray(r.user_ids) && r.user_ids.includes(me.id);
      chip.className = 'reaction-chip' + (mine ? ' mine' : '');
      chip.textContent = r.emoji + ' ' + r.count;
      chip.onclick = (e) => { e.stopPropagation(); toggleReaction(m.id, r.emoji); };
      rxnsHost.appendChild(chip);
    }
    col.appendChild(rxnsHost);
  }
  div.appendChild(col);

  // Hover-revealed actions: 😊 react, Reply, Edit, Delete.
  if (!isDeleted) {
    const actions = document.createElement('div');
    actions.className = 'row-actions-msg';
    const reactBtn = document.createElement('button');
    reactBtn.title = 'React'; reactBtn.textContent = '😊';
    reactBtn.onclick = (e) => { e.stopPropagation(); openEmojiPicker(reactBtn, m); };
    actions.appendChild(reactBtn);
    const replyBtn = document.createElement('button');
    replyBtn.title = 'Reply'; replyBtn.textContent = '↩';
    replyBtn.onclick = (e) => { e.stopPropagation(); startReply(m); };
    actions.appendChild(replyBtn);
    if (isMine && messageWithinEditWindow(m)) {
      const editBtn = document.createElement('button');
      editBtn.title = 'Edit'; editBtn.textContent = '✎';
      editBtn.onclick = (e) => { e.stopPropagation(); startEdit(m); };
      actions.appendChild(editBtn);
      const delBtn = document.createElement('button');
      delBtn.className = 'danger'; delBtn.title = 'Delete'; delBtn.textContent = '🗑';
      delBtn.onclick = (e) => { e.stopPropagation(); deleteMessage(m); };
      actions.appendChild(delBtn);
    }
    div.appendChild(actions);
  }

  t.appendChild(div);
}

const EMOJI_PALETTE = [
  '👍','👎','❤️','🔥','🎉','👏','🙏','😂',
  '😄','😎','😮','😢','😡','🤔','💯','✅',
  '❌','⏰','📌','📷','🚚','🛠️','💪','💰',
];
let activeEmojiPicker = null;
function openEmojiPicker(anchorBtn, m) {
  closeEmojiPicker();
  const picker = document.createElement('div');
  picker.className = 'emoji-picker';
  for (const e of EMOJI_PALETTE) {
    const b = document.createElement('button');
    b.textContent = e;
    b.onclick = (ev) => {
      ev.stopPropagation();
      toggleReaction(m.id, e);
      closeEmojiPicker();
    };
    picker.appendChild(b);
  }
  document.body.appendChild(picker);
  // Position above the button.
  const r = anchorBtn.getBoundingClientRect();
  const pickerW = 32 * 8 + 7 * 4 + 16;
  picker.style.left = Math.max(8, r.right - pickerW) + 'px';
  picker.style.top = Math.max(8, r.top - 240) + window.scrollY + 'px';
  activeEmojiPicker = picker;
  setTimeout(() => {
    document.addEventListener('click', closeEmojiPicker, { once: true });
  }, 0);
}
function closeEmojiPicker() {
  if (activeEmojiPicker) { activeEmojiPicker.remove(); activeEmojiPicker = null; }
}

async function toggleReaction(messageId, emoji) {
  try {
    await api('/api/v1/chat/messages/' + messageId + '/reactions', {
      method: 'POST', body: { emoji },
    });
  } catch (e) {
    alert('Reaction failed: ' + e.message);
  }
}

function messageWithinEditWindow(m) {
  if (!m.created_at) return false;
  const d = new Date(m.created_at.replace(' ', 'T') + 'Z');
  return (Date.now() - d.getTime()) <= 10000;
}

let replyingTo = null;
let editingMessage = null;

function startReply(m) {
  replyingTo = m; editingMessage = null;
  document.getElementById('composer-input').focus();
  refreshComposerChips();
}

function startEdit(m) {
  editingMessage = m; replyingTo = null;
  const ta = document.getElementById('composer-input');
  ta.value = m.body; autoGrow(ta); ta.focus();
  refreshComposerChips();
}

function refreshComposerChips() {
  let host = document.getElementById('composer-chips');
  if (!host) {
    host = document.createElement('div');
    host.id = 'composer-chips';
    host.style.cssText = 'padding:6px 14px; background:#f1f5f9; font-size:12px; color:var(--muted); display:flex; gap:8px; align-items:center;';
    const c = document.getElementById('composer');
    c.parentNode.insertBefore(host, c);
  }
  host.innerHTML = '';
  if (replyingTo) {
    host.style.display = 'flex';
    host.innerHTML = `<div style="border-left:3px solid var(--primary);padding-left:6px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
      <strong>Reply to ${replyingTo.sender?.display_name || ''}:</strong> ${replyingTo.body}
    </div><button onclick="cancelChip()" style="background:transparent;border:0;cursor:pointer;font-size:14px;">✕</button>`;
  } else if (editingMessage) {
    host.style.display = 'flex';
    host.innerHTML = `<div style="flex:1">Editing message</div>
      <button onclick="cancelChip()" style="background:transparent;border:0;cursor:pointer;font-size:14px;">✕</button>`;
  } else {
    host.style.display = 'none';
  }
}

function cancelChip() {
  if (editingMessage) {
    document.getElementById('composer-input').value = '';
    autoGrow(document.getElementById('composer-input'));
  }
  replyingTo = null; editingMessage = null;
  refreshComposerChips();
}

async function deleteMessage(m) {
  if (!confirm('Delete this message?')) return;
  try {
    await api('/api/v1/chat/messages/' + m.id, { method: 'DELETE' });
  } catch (e) {
    alert('Delete failed: ' + e.message);
  }
}

// Pick → upload as multipart. Sends any current draft as the body and
// preserves the active reply-to. Skipped while editing — you can't swap
// the attachment of an already-sent message.
async function onAttachmentPicked(ev) {
  const input = ev.target;
  const file = input.files && input.files[0];
  input.value = '';
  if (!file || !activeConvId) return;
  if (editingMessage) return;

  const ta = document.getElementById('composer-input');
  const body = ta.value.trim();
  const replyId = replyingTo ? replyingTo.id : null;

  const fd = new FormData();
  if (body) fd.append('body', body);
  if (replyId != null) fd.append('reply_to_message_id', String(replyId));
  fd.append('file', file, file.name);

  ta.disabled = true;
  document.getElementById('send-btn').disabled = true;
  try {
    const r = await fetch('/api/v1/chat/conversations/' + activeConvId + '/messages/upload', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token },
      body: fd,
    });
    if (!r.ok) {
      let msg = 'Upload failed';
      try { msg = (await r.json()).error || msg; } catch (e) {}
      alert(msg);
      return;
    }
    ta.value = ''; autoGrow(ta);
    replyingTo = null;
    refreshComposerChips();
  } catch (e) {
    alert('Upload failed: ' + e.message);
  } finally {
    ta.disabled = false;
    document.getElementById('send-btn').disabled = false;
    ta.focus();
  }
}

// Browser image tags can't carry custom headers. We fetch each protected
// attachment URL via authenticated JS and swap in a blob URL once it
// loads. Cache by URL so the same image isn't refetched on re-render.
const blobCache = {};
function loadAttachmentImage(imgEl, url) {
  if (blobCache[url]) { imgEl.src = blobCache[url]; return; }
  fetch(url, { headers: { 'Authorization': 'Bearer ' + token } })
    .then(r => r.ok ? r.blob() : null)
    .then(b => {
      if (!b) return;
      const u = URL.createObjectURL(b);
      blobCache[url] = u;
      imgEl.src = u;
    });
}

async function sendMessage() {
  if (!activeConvId) return;
  const ta = document.getElementById('composer-input');
  const body = ta.value.trim();
  if (!body) return;
  ta.disabled = true;
  document.getElementById('send-btn').disabled = true;
  try {
    if (editingMessage) {
      await api('/api/v1/chat/messages/' + editingMessage.id, {
        method: 'PATCH', body: { body },
      });
      editingMessage = null;
    } else {
      const payload = { body };
      if (replyingTo) payload.reply_to_message_id = replyingTo.id;
      await api('/api/v1/chat/conversations/' + activeConvId + '/messages', {
        method: 'POST', body: payload,
      });
      replyingTo = null;
    }
    refreshComposerChips();
    ta.value = ''; autoGrow(ta);
  } catch (e) {
    alert('Send failed: ' + e.message);
  } finally {
    ta.disabled = false;
    document.getElementById('send-btn').disabled = false;
    ta.focus();
  }
}

function onComposerKey(ev) {
  // Default behavior: Enter sends, Shift+Enter inserts newline. Toggle in
  // the chat header "..." menu flips this for users who prefer composing
  // multi-line drafts before sending.
  const enterToSend = localStorage.getItem('astra_enter_to_send') !== '0';
  if (enterToSend && ev.key === 'Enter' && !ev.shiftKey) {
    ev.preventDefault();
    sendMessage();
  }
}

function toggleEnterToSend() {
  const cur = localStorage.getItem('astra_enter_to_send') !== '0';
  const next = !cur;
  localStorage.setItem('astra_enter_to_send', next ? '1' : '0');
  document.getElementById('enter-toggle-label').textContent =
    'Enter to send: ' + (next ? 'On' : 'Off');
}

function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(140, el.scrollHeight) + 'px';
}

function relTime(s) {
  if (!s) return '';
  const d = s.includes('T') ? new Date(s) : new Date(s.replace(' ', 'T') + 'Z');
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h';
  if (diff < 7 * 86400) return Math.floor(diff / 86400) + 'd';
  return d.toLocaleDateString();
}

// ---------------- Modals ----------------

// New-chat picker — single multi-select sheet. 1 picked → DM, 2+ → group
// (auto-named from selected first names; user can edit before submitting).
let newChatPickedOrder = [];
let newChatEmployeesById = {};
let newChatUserEditedTitle = false;

async function openNewChat() {
  newChatPickedOrder = [];
  newChatUserEditedTitle = false;
  document.getElementById('new-group-title').value = '';
  document.getElementById('new-group-name-row').style.display = 'none';
  document.getElementById('new-confirm-btn').textContent = 'Start';
  document.getElementById('new-confirm-btn').disabled = true;

  const grid = document.getElementById('new-emp-grid');
  grid.innerHTML = 'Loading…';
  document.getElementById('modal-newchat').classList.add('show');
  document.getElementById('new-chat-fab').classList.add('hidden');
  const j = await api('/api/v1/chat/employees');
  newChatEmployeesById = {};
  grid.innerHTML = '';
  for (const e of j.employees) {
    newChatEmployeesById[e.id] = e;
    const card = document.createElement('div');
    card.className = 'emp-card';
    card.dataset.empId = e.id;
    card.onclick = () => {
      const picked = newChatPickedOrder.includes(e.id);
      onNewChatPickToggle(e.id, !picked);
      card.classList.toggle('selected', !picked);
    };
    const av = document.createElement('div');
    av.className = 'av-lg';
    av.style.background = avatarColorForSender(e.id);
    av.textContent = (e.display_name.split(' ').slice(0, 2).map(p => p[0] || '').join('').toUpperCase()) || '?';
    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = e.display_name;
    card.append(av, name);
    grid.appendChild(card);
  }
}

function onNewChatPickToggle(id, picked) {
  if (picked) {
    if (!newChatPickedOrder.includes(id)) newChatPickedOrder.push(id);
  } else {
    newChatPickedOrder = newChatPickedOrder.filter(x => x !== id);
  }
  refreshNewChatUI();
}

function newChatAutoTitle() {
  return newChatPickedOrder
    .map(id => (newChatEmployeesById[id] || {}).display_name)
    .filter(Boolean)
    .join(', ');
}

function refreshNewChatUI() {
  const isGroup = newChatPickedOrder.length >= 2;
  document.getElementById('new-group-name-row').style.display = isGroup ? '' : 'none';
  const titleField = document.getElementById('new-group-title');
  if (isGroup && !newChatUserEditedTitle) {
    titleField.value = newChatAutoTitle();
  }
  titleField.oninput = () => {
    newChatUserEditedTitle = titleField.value.length > 0
      && titleField.value !== newChatAutoTitle();
    if (titleField.value === '') newChatUserEditedTitle = false;
    refreshConfirmBtn();
  };
  refreshConfirmBtn();
}

function refreshConfirmBtn() {
  const btn = document.getElementById('new-confirm-btn');
  const n = newChatPickedOrder.length;
  if (n === 0) { btn.disabled = true; btn.textContent = 'Start'; return; }
  if (n === 1) { btn.disabled = false; btn.textContent = 'Start'; return; }
  btn.textContent = 'Create';
  const title = newChatUserEditedTitle
    ? document.getElementById('new-group-title').value.trim()
    : newChatAutoTitle();
  btn.disabled = title.length === 0;
}

async function confirmNewChat() {
  const n = newChatPickedOrder.length;
  if (n === 0) return;
  try {
    let body;
    if (n === 1) {
      body = { kind: 'dm', user_id: newChatPickedOrder[0] };
    } else {
      const title = newChatUserEditedTitle
        ? document.getElementById('new-group-title').value.trim()
        : newChatAutoTitle();
      body = { kind: 'group', title, user_ids: newChatPickedOrder.slice() };
    }
    const j = await api('/api/v1/chat/conversations', {
      method: 'POST', body,
    });
    closeModal('modal-newchat');
    await loadConversations();
    openConversation(j.conversation.id);
  } catch (e) {
    alert('Failed: ' + e.message);
  }
}

function closeModal(id) {
  document.getElementById(id).classList.remove('show');
  // Bring the "+" FAB back when the New Chat modal closes.
  if (id === 'modal-newchat') {
    document.getElementById('new-chat-fab').classList.remove('hidden');
  }
}

// ---------------- SSE ----------------

let sseRetryDelay = 1000;
function connectSSE() {
  if (!token) return;
  if (sse) { try { sse.close(); } catch (e) {} }
  document.getElementById('conn').classList.add('show');
  sse = new EventSource('/api/v1/chat/sse?token=' + encodeURIComponent(token));
  sse.addEventListener('hello', () => {
    sseRetryDelay = 1000;
    document.getElementById('conn').classList.remove('show');
  });
  sse.onmessage = (ev) => {
    document.getElementById('conn').classList.remove('show');
    handleSSE(JSON.parse(ev.data));
  };
  sse.onerror = () => {
    document.getElementById('conn').classList.add('show');
    try { sse.close(); } catch (e) {}
    sse = null;
    setTimeout(connectSSE, sseRetryDelay);
    sseRetryDelay = Math.min(15000, sseRetryDelay * 2);
  };
}

function handleSSE(ev) {
  if (ev.type === 'message') {
    const m = ev.data;
    if (m.conversation_id === activeConvId) {
      messageCache[activeConvId] = (messageCache[activeConvId] || []).concat([m]);
      appendMessage(m);
      const t = document.getElementById('thread');
      t.scrollTop = t.scrollHeight;
      if (m.sender_id !== me.id) {
        api('/api/v1/chat/conversations/' + activeConvId + '/read', {
          method: 'POST', body: { message_id: m.id },
        }).catch(() => {});
      }
    }
    // Update conversation list (move to top, set preview).
    let conv = conversations.find(c => c.id === m.conversation_id);
    if (!conv) {
      loadConversations();
      return;
    }
    conv.last_message_at = m.created_at;
    conv.last_message_preview = m.body.slice(0, 140);
    conv.last_message_sender_id = m.sender_id;
    if (m.conversation_id !== activeConvId && m.sender_id !== me.id) {
      conv.unread_count = (conv.unread_count || 0) + 1;
    }
    conversations = [conv].concat(conversations.filter(c => c.id !== conv.id));
    renderConvList();
  } else if (ev.type === 'message_updated') {
    const m = ev.data;
    const cache = messageCache[m.conversation_id] || [];
    const idx = cache.findIndex(x => x.id === m.id);
    if (idx >= 0) {
      cache[idx] = m;
      messageCache[m.conversation_id] = cache;
      if (m.conversation_id === activeConvId) renderThread();
    }
    // Update list preview if needed.
    const conv = conversations.find(c => c.id === m.conversation_id);
    if (conv && conv.last_message_sender_id === m.sender_id) {
      conv.last_message_preview = (m.deleted || m.deleted_at) ? 'Message deleted' : m.body.slice(0, 140);
      renderConvList();
    }
  } else if (ev.type === 'conversation_created') {
    loadConversations();
  } else if (ev.type === 'conversation_deleted') {
    const cid = (ev.data || {}).conversation_id;
    if (cid != null) {
      conversations = conversations.filter(c => c.id !== cid);
      messageCache[cid] = undefined;
      if (activeConvId === cid) closeThread();
      renderConvList();
    }
  } else if (ev.type === 'notification') {
    if (Notification && Notification.permission === 'granted' && ev.data.kind === 'chat_message'
        && (ev.data.data || {}).conversation_id !== activeConvId) {
      try { new Notification(ev.data.title || 'Astra Chat', { body: ev.data.body || '' }); } catch (e) {}
    }
  }
}

if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
  setTimeout(() => { Notification.requestPermission(); }, 500);
}

boot();
</script>
</body>
</html>
"""


def register(rt):
    @rt("/chat")
    def chat_page():
        return HTMLResponse(_PAGE)
