/* staging_edit_modal.js — Staging record editor.
 *
 * Consumes Portal.Modal. Schema-driven; backend is /portal/staging/<id> (GET)
 * and /portal/staging/<id>/save (POST). Save sends only the diff. Server is
 * source of truth for derived numbers — modal recomputes a few client-side
 * for instant feedback, then re-displays whatever the server returns.
 *
 * Usage:
 *   StagingEditModal.open('3692314000021335612', { onSaved: () => location.reload() });
 */

(function () {
  if (window.StagingEditModal) return;
  if (!window.Portal || !window.Portal.Modal) {
    console.error('[StagingEditModal] portal_modal.js must load first');
    return;
  }
  const { h, field, toast } = Portal.Modal;

  // ---------- field registry ----------
  // Each entry: { key, label, type, options?, hint?, readonly?, full? }
  // type: text, textarea, money, integer, picklist, date, time, people,
  //       chip-date (one-tap "today" toggle), readonly, action-button
  const SECTIONS = {
    general: {
      label: 'General',
      groups: [
        { title: 'Status', fields: [
          { key: 'Staging_Status', label: 'Status', type: 'picklist',
            options: ['Active', 'Inactive', 'Inquired'] },
          { key: 'Staging_Furniture_Quality', label: 'Furniture Quality', type: 'picklist',
            options: ['Regular', 'Premium'],
            hint: 'Premium hides regular items in Design view' },
          { key: 'Staging_Type', label: 'Type', type: 'picklist',
            options: ['Regular', 'Non-Designer'] },
          { key: 'Staging_Complexity', label: 'Complexity', type: 'picklist',
            options: ['Normal', 'Difficult'] },
          { key: 'Is_Showcase', label: 'Showcase', type: 'picklist',
            options: ['', 'Yes', 'No'] },
        ]},
        { title: 'Property', fields: [
          { key: 'Staging_Address', label: 'Property Address', type: 'text', full: true },
          { key: 'Staging_Display_Name', label: 'Display Name', type: 'readonly',
            hint: 'Auto-derived' },
          { key: 'Property_Type', label: 'Property Type', type: 'picklist',
            options: ['', 'House', 'Townhouse', 'Condo'] },
          { key: 'Occupancy_Type', label: 'Occupancy', type: 'picklist',
            options: ['', 'Occupied', 'Vacant'] },
        ]},
        { title: 'Dates', fields: [
          { key: 'Staging_Date', label: 'Staging Date', type: 'date' },
          { key: 'Staging_ETA', label: 'Staging ETA', type: 'time' },
          { key: 'Staging_Date_Flexible', label: 'Date Flexible', type: 'picklist',
            options: ['', 'Yes', 'No'] },
          { key: 'Staging_Term', label: 'Term (days)', type: 'picklist',
            options: ['', '30','45','60','75','90','105','120','135','150','165','180','210','240','270','300','360'] },
          { key: 'Destaging_Date', label: 'Destaging Date', type: 'date' },
          { key: 'Destaging_ETA', label: 'Destaging ETA', type: 'time' },
          { key: 'Destaging_Date_Flexible', label: 'Destage Flexible', type: 'picklist',
            options: ['', 'Yes', 'No'] },
        ]},
        { title: 'Consultation', fields: [
          { key: 'Consultation_Type', label: 'Consultation Type', type: 'picklist',
            options: ['', 'In Person', 'Video Call'] },
          { key: 'Consultation_Date_and_Time', label: 'Consultation Date/Time', type: 'datetime' },
          { key: 'Consultation_Stager1', label: 'Consultation Stager', type: 'people',
            roles: ['stager'], single: true },
          { key: 'Consultation_Notes_Complete_Time', label: 'Notes Complete', type: 'readonly',
            hint: 'Auto-stamped from consultation flow' },
        ]},
        { title: 'Team', fields: [
          { key: 'Stager', label: 'Stagers', type: 'people', roles: ['stager'] },
          { key: 'Staging_Movers', label: 'Staging Movers', type: 'people', roles: ['mover'] },
          { key: 'Destaging_Movers', label: 'Destaging Movers', type: 'people', roles: ['mover'] },
          { key: 'Furniture_Locations', label: 'Furniture Locations', type: 'text', full: true,
            hint: 'Comma-separated for multi-warehouse' },
          { key: 'Design_Items_Matched_Date', label: 'Design Matched', type: 'readonly' },
        ]},
      ],
    },

    customer: {
      label: 'Customer',
      groups: [
        { title: 'Identity', fields: [
          { key: 'Customer_First_Name', label: 'First Name', type: 'text' },
          { key: 'Customer_Last_Name', label: 'Last Name', type: 'text' },
          { key: 'Customer_Email', label: 'Email', type: 'text' },
          { key: 'Customer_Phone', label: 'Phone', type: 'text' },
          { key: 'Quote', label: 'Inquiry', type: 'readonly', hint: 'Linked Quote record' },
          { key: 'Customer_CRM', label: 'CRM Lead', type: 'readonly',
            hint: 'Linked Zoho CRM lead (read-only here)' },
        ]},
        { title: 'Profile', fields: [
          { key: 'Customer_Attributes', label: 'Customer Attributes', type: 'tags', full: true,
            options: ['Block', 'Demanding', 'Delayed payment', 'Non-payment', 'Low-budget', 'Picky (style/condition)'] },
          { key: 'Customer_Notes', label: 'Customer Notes', type: 'textarea', full: true },
        ]},
      ],
    },

    moving: {
      label: 'Moving',
      groups: [
        { title: 'Logistics', fields: [
          { key: 'Total_Item_Number', label: 'Total Items', type: 'integer',
            hint: 'Auto-fills from Design when ready' },
          { key: 'Driving_Time', label: 'Driving Time (mins)', type: 'integer' },
          { key: 'Dock', label: 'Dock', type: 'picklist', options: ['', 'Dock 1', 'Dock 2'] },
        ]},
        { title: 'Property Access — Staging', fields: [
          { key: 'Person_To_Provide_Access_for_Staging', label: 'Access Person', type: 'text' },
          { key: 'Lockbox_Code_for_Staging', label: 'Lockbox Code', type: 'text' },
          { key: 'Elevator_Start_Time', label: 'Elevator Start', type: 'time' },
          { key: 'Elevator_Finish_Time', label: 'Elevator Finish', type: 'time' },
          { key: 'Staging_Moving_Instructions', label: 'Staging Move Instructions',
            type: 'textarea', full: true },
        ]},
        { title: 'Property Access — Destaging', fields: [
          { key: 'Person_To_Provide_Access_for_Destaging', label: 'Access Person', type: 'text' },
          { key: 'Lockbox_Code_for_Destaging', label: 'Lockbox Code', type: 'text' },
          { key: 'Destaging_Moving_Instructions', label: 'Destage Move Instructions',
            type: 'textarea', full: true },
        ]},
      ],
    },

    design: {
      label: 'Design',
      groups: [
        { title: 'Notes', fields: [
          { key: 'General_Notes', label: 'General Notes', type: 'textarea', full: true,
            actions: [{ label: '+ Date stamp', op: 'date-stamp' }] },
          { key: 'Consultation_Instructions', label: 'Consultation Instructions',
            type: 'textarea', full: true },
          { key: 'Design_Notes', label: 'Design Notes', type: 'textarea', full: true,
            hint: 'Plain text for now (richtext coming later)' },
          { key: 'Staging_Feedback', label: 'Staging Feedback', type: 'textarea', full: true },
        ]},
        { title: 'Settings', fields: [
          { key: 'Lock_Design', label: 'Lock Design', type: 'picklist',
            options: ['', 'Yes', 'No'] },
          { key: 'Show_Design_To_Customer', label: 'Show Design to Customer', type: 'picklist',
            options: ['', 'Yes', 'No'] },
        ]},
        { title: 'Milestones', fields: [
          { key: 'Check_Basement_Furniture_Size_Date', label: 'Basement Check', type: 'chip-date' },
          { key: 'Staging_Furniture_Design_Finish_Date', label: 'Design Done', type: 'chip-date' },
          { key: 'Staging_Accessories_Packing_Finish_Date', label: 'Acc. Packing Done', type: 'chip-date' },
        ]},
      ],
    },

    payment: {
      label: '$ Payment',
      groups: [
        { title: 'Quoted', fields: [
          { key: 'Total_Staging_Fee',  label: 'Total Staging Fee',  type: 'money' },
          { key: 'Initial_Staging_Fee',label: 'Initial Staging Fee',type: 'money' },
          { key: 'Photography_Fee',    label: 'Photography Fee',    type: 'money' },
          { key: 'Moving_Fee',         label: 'Moving Fee',         type: 'money' },
          { key: 'Monthly_Extension_Fee', label: 'Monthly Extension Fee', type: 'money' },
          { key: 'Total_Extension_Fee',label: 'Total Extension Fee',type: 'readonly',
            hint: 'months × monthly' },
        ]},
        { title: 'Deposits', fields: [
          { key: 'Deposit_Amount',  label: 'Deposit Amount', type: 'money' },
          { key: 'Security_Deposit',label: 'Security Deposit (Pet/Damage)', type: 'money' },
          { key: 'Pay_by_Cash',     label: 'Pay by Cash', type: 'picklist',
            options: ['', 'true', 'false'] },
        ]},
        { title: 'Totals (auto)', fields: [
          { key: 'Total_Amount', label: 'Total Amount', type: 'readonly' },
          { key: 'HST',          label: 'HST',          type: 'readonly' },
          { key: 'Paid_Amount',  label: 'Paid Amount',  type: 'readonly',
            hint: 'Sum of Payment records' },
          { key: 'Owing_Amount', label: 'Owing Amount', type: 'readonly' },
        ]},
        { title: 'Invoice', fields: [
          { key: 'Invoice_Sent_Date', label: 'Invoice Sent Date', type: 'chip-date' },
        ], rowActions: [
          { label: 'Generate invoice', op: 'preview', kind: 'pill' },
          { label: 'Record payment',   op: 'preview', kind: 'pill' },
        ]},
      ],
    },

    listing: {
      label: 'Listing',
      groups: [
        { title: 'MLS', fields: [
          { key: 'MLS', label: 'MLS', type: 'text' },
          { key: 'Listing_Price', label: 'Listing Price', type: 'money' },
          { key: 'Days_On_Market', label: 'Days on Market', type: 'readonly',
            hint: 'Derived from MLS' },
        ]},
        { title: 'Pictures (server-hosted)', fields: [
          { key: 'Pictures_Folder', label: 'Pictures Folder', type: 'readonly-link',
            hint: 'Will move from Drive to server' },
          { key: 'Before_Picture_Upload_Date', label: 'Before Pictures', type: 'chip-date' },
          { key: 'After_Picture_Upload_Date',  label: 'After Pictures',  type: 'chip-date' },
        ], rowActions: [
          { label: 'Search HouseSigma', op: 'housesigma', kind: 'pill' },
        ]},
      ],
    },

    notify: {
      label: 'Notify',
      groups: [
        { title: 'Templates', fields: [
          { key: 'Staging_Item_List', label: 'Staging Item List', type: 'textarea', full: true,
            actions: [{ label: 'Load default', op: 'preview' }] },
          { key: 'Seller_To_Do_List', label: 'Seller To-Do List', type: 'textarea', full: true,
            hint: 'Use "N/A" for not applicable' },
        ]},
        { title: 'Customer Touchpoints', fields: [
          { key: 'WhatsApp_Group_Created_Date', label: 'WhatsApp Group', type: 'chip-date' },
          { key: 'Consultation_Confirmation_Email_Sent_Date', label: 'Consultation Confirm', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Next_Steps_Email_Sent_Date', label: 'Next Steps', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Extension_Email_Sent_Date', label: 'Extension', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Destaging_Confirmation_Email_Sent_Date', label: 'Destaging Confirm', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Staging_Completion_Confirmation_Sent_Date', label: 'Staging Done Notice', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Destaging_Completion_Confirmation_Sent_Date', label: 'Destaging Done Notice', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Staging_Review_Request_Sent_Date', label: 'Staging Review Ask', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Destaging_Review_Request_Sent_Date', label: 'Destaging Review Ask', type: 'chip-date',
            sendAction: 'preview' },
          { key: 'Customer_Acknowledged_Time', label: 'Customer Acknowledged', type: 'readonly' },
        ]},
      ],
    },
  };

  // ---------- value adapters ----------
  function todayMDY() {
    const d = new Date();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${m}/${day}/${d.getFullYear()}`;
  }
  function mdyToISO(mdy) {
    if (!mdy || typeof mdy !== 'string') return '';
    const m = mdy.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    if (!m) return '';
    return `${m[3]}-${m[1].padStart(2,'0')}-${m[2].padStart(2,'0')}`;
  }
  function isoToMDY(iso) {
    if (!iso) return '';
    const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (!m) return '';
    return `${m[2]}/${m[3]}/${m[1]}`;
  }
  function fmtMoney(v) {
    const n = parseFloat(v);
    if (!isFinite(n)) return '';
    return n.toLocaleString('en-CA', { style: 'currency', currency: 'CAD' });
  }

  // ---------- field renderers ----------
  function renderField(f, state, rec) {
    const cur = state.values[f.key];
    let inputEl;

    switch (f.type) {
      case 'text':
        inputEl = h('input', { type: 'text', value: cur || '' });
        inputEl.addEventListener('input', () => state.set(f.key, inputEl.value));
        break;

      case 'integer':
        inputEl = h('input', { type: 'number', step: '1', value: cur || '' });
        inputEl.addEventListener('input', () => state.set(f.key, inputEl.value));
        break;

      case 'money':
        inputEl = h('input', { type: 'number', step: '0.01', value: cur || '' });
        inputEl.addEventListener('input', () => state.set(f.key, inputEl.value));
        // hint to show formatted value when not focused
        inputEl.addEventListener('blur', () => {
          if (inputEl.value) inputEl.title = fmtMoney(inputEl.value);
        });
        break;

      case 'textarea': {
        const ta = h('textarea', { rows: 5 }, cur || '');
        ta.addEventListener('input', () => state.set(f.key, ta.value));
        inputEl = ta;
        break;
      }

      case 'picklist': {
        const sel = h('select');
        f.options.forEach(o => {
          const opt = h('option', { value: o, selected: (cur || '') === o }, o || '—');
          sel.appendChild(opt);
        });
        sel.addEventListener('change', () => state.set(f.key, sel.value));
        inputEl = sel;
        break;
      }

      case 'date': {
        inputEl = h('input', { type: 'date', value: mdyToISO(cur || '') });
        inputEl.addEventListener('input', () => state.set(f.key, isoToMDY(inputEl.value)));
        break;
      }

      case 'time': {
        // accept "HH:MM:SS" or "HH:MM"
        const v = cur ? String(cur).slice(0, 5) : '';
        inputEl = h('input', { type: 'time', value: v });
        inputEl.addEventListener('input', () => state.set(f.key, inputEl.value ? inputEl.value + ':00' : ''));
        break;
      }

      case 'datetime': {
        // Stored as "MM/DD/YYYY HH:MM:SS"
        const m = (cur || '').match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{2}):(\d{2})/);
        const isoLocal = m ? `${m[3]}-${m[1].padStart(2,'0')}-${m[2].padStart(2,'0')}T${m[4]}:${m[5]}` : '';
        inputEl = h('input', { type: 'datetime-local', value: isoLocal });
        inputEl.addEventListener('input', () => {
          const v = inputEl.value; // YYYY-MM-DDTHH:MM
          if (!v) { state.set(f.key, ''); return; }
          const mm = v.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
          if (mm) state.set(f.key, `${mm[2]}/${mm[3]}/${mm[1]} ${mm[4]}:${mm[5]}:00`);
        });
        break;
      }

      case 'chip-date': {
        const wrap = h('div', { class: 'pm-chips' });
        const isDone = !!(cur && String(cur).trim());
        const chip = h('button', {
          type: 'button',
          class: 'pm-chip' + (isDone ? ' on' : ' muted'),
          onclick: () => {
            const newVal = chip.classList.contains('on') ? '' : todayMDY();
            state.set(f.key, newVal);
            chip.classList.toggle('on', !!newVal);
            chip.classList.toggle('muted', !newVal);
            chip.firstChild.textContent = newVal ? '✓ ' + newVal : '○ Mark today';
          },
        }, isDone ? '✓ ' + cur : '○ Mark today');
        wrap.appendChild(chip);
        if (f.sendAction) {
          const send = h('button', {
            type: 'button', class: 'pm-pill-btn muted',
            onclick: () => Portal.Modal.toast('Email send not wired yet — design preview', 'info'),
          }, '✉ Send');
          wrap.appendChild(send);
        }
        inputEl = wrap;
        break;
      }

      case 'people': {
        const roster = state.roster || [];
        const allowed = roster.filter(p => !f.roles || f.roles.some(r => p.roles.includes(r)));
        const arr = Array.isArray(cur) ? cur.slice() : [];
        const wrap = h('div', { class: 'pm-people-picker' });
        function rerender() {
          wrap.innerHTML = '';
          arr.forEach((name, i) => {
            const chip = h('span', { class: 'pm-chip on' }, name,
              h('span', {
                class: 'pm-chip-x',
                onclick: () => { arr.splice(i, 1); state.set(f.key, arr.slice()); rerender(); },
              }, ' ×'));
            wrap.appendChild(chip);
          });
          const remaining = allowed.filter(p => !arr.includes(p.name));
          if (!f.single || arr.length === 0) {
            const sel = h('select');
            sel.appendChild(h('option', { value: '' }, '+ add'));
            remaining.forEach(p => sel.appendChild(h('option', { value: p.name }, p.name)));
            sel.addEventListener('change', () => {
              if (!sel.value) return;
              if (f.single) arr.length = 0;
              arr.push(sel.value);
              state.set(f.key, arr.slice());
              rerender();
            });
            wrap.appendChild(sel);
          }
        }
        rerender();
        inputEl = wrap;
        break;
      }

      case 'tags': {
        const arr = Array.isArray(cur) ? cur.slice() : [];
        const wrap = h('div', { class: 'pm-people-picker' });
        function rerender() {
          wrap.innerHTML = '';
          arr.forEach((tag, i) => {
            const chip = h('span', { class: 'pm-chip on' }, tag,
              h('span', {
                class: 'pm-chip-x',
                onclick: () => { arr.splice(i, 1); state.set(f.key, arr.slice()); rerender(); },
              }, ' ×'));
            wrap.appendChild(chip);
          });
          const remaining = (f.options || []).filter(o => !arr.includes(o));
          if (remaining.length) {
            const sel = h('select');
            sel.appendChild(h('option', { value: '' }, '+ add tag'));
            remaining.forEach(o => sel.appendChild(h('option', { value: o }, o)));
            sel.addEventListener('change', () => {
              if (!sel.value) return;
              arr.push(sel.value);
              state.set(f.key, arr.slice());
              rerender();
            });
            wrap.appendChild(sel);
          }
        }
        rerender();
        inputEl = wrap;
        break;
      }

      case 'readonly':
        inputEl = h('div', { class: 'readonly' }, (cur && String(cur)) || '—');
        break;

      case 'readonly-link': {
        const v = cur && String(cur);
        if (v && /^https?:\/\//i.test(v)) {
          inputEl = h('div', { class: 'readonly' },
            h('a', { href: v, target: '_blank', rel: 'noopener' }, v));
        } else {
          inputEl = h('div', { class: 'readonly' }, v || '—');
        }
        break;
      }

      default:
        inputEl = h('div', { class: 'readonly' }, '(unsupported: ' + f.type + ')');
    }

    const wrap = field(f.label, inputEl, { full: !!f.full, hint: f.hint });
    // Inline per-field actions (e.g. "+ Date stamp" on General Notes)
    if (Array.isArray(f.actions) && f.actions.length) {
      const row = h('div', { class: 'pm-row-actions' });
      f.actions.forEach(a => {
        row.appendChild(h('button', {
          type: 'button', class: 'pm-pill-btn muted',
          onclick: () => handleAction(a, f, state, inputEl),
        }, a.label));
      });
      wrap.appendChild(row);
    }
    return wrap;
  }

  function handleAction(a, f, state, inputEl) {
    if (a.op === 'date-stamp' && f.type === 'textarea') {
      const stamp = '[' + new Date().toISOString().slice(0, 10) + '] ';
      const cur = state.values[f.key] || '';
      const next = stamp + (cur ? '\n' + cur : '');
      state.set(f.key, next);
      inputEl.value = next;
      inputEl.focus();
      return;
    }
    if (a.op === 'preview') {
      Portal.Modal.toast(a.label + ' — design preview, not wired yet', 'info');
      return;
    }
    if (a.op === 'housesigma') {
      // Open HouseSigma search for the address. Read-only here since the
      // user said HouseSigma URL will be auto-found, not manual.
      const addr = state.values.Staging_Address || '';
      const url = 'https://housesigma.com/search?q=' + encodeURIComponent(addr);
      window.open(url, '_blank', 'noopener');
      return;
    }
    Portal.Modal.toast('Action not implemented', 'warn');
  }

  function renderGroup(group, state, rec) {
    const out = document.createDocumentFragment();
    if (group.title) out.appendChild(h('div', { class: 'pm-section' }, group.title));
    const grid = h('div', { class: 'pm-grid' });
    group.fields.forEach(f => grid.appendChild(renderField(f, state, rec)));
    out.appendChild(grid);
    if (Array.isArray(group.rowActions) && group.rowActions.length) {
      const row = h('div', { class: 'pm-row-actions' });
      group.rowActions.forEach(a => {
        row.appendChild(h('button', {
          type: 'button', class: 'pm-pill-btn',
          onclick: () => handleAction(a, {}, state),
        }, a.label));
      });
      out.appendChild(row);
    }
    return out;
  }

  // ---------- main: open() ----------
  async function openModal(stagingId, opts) {
    opts = opts || {};
    // Fetch first — fast on localhost, no placeholder needed. On failure we
    // show a toast and bail. Caller can retry.
    let rec;
    try {
      const r = await fetch('/portal/staging/' + encodeURIComponent(stagingId), {
        headers: { 'Accept': 'application/json' },
      });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      rec = await r.json();
    } catch (e) {
      Portal.Modal.toast('Could not load staging: ' + e.message, 'error');
      return;
    }

    // modalRef forward-references the live modal so input listeners can
    // reach it after Portal.Modal.open() returns. Listeners are attached
    // during render, which happens *inside* the open() call.
    const modalRef = { value: null };

    const state = {
      values: { ...rec.values },
      original: { ...rec.values },
      roster: rec.roster || [],
      dirty: new Set(),
      set(k, v) {
        const old = JSON.stringify(this.original[k] ?? '');
        const cur = JSON.stringify(v ?? '');
        if (cur === old) this.dirty.delete(k);
        else this.dirty.add(k);
        this.values[k] = v;
        const live = modalRef.value;
        if (!live) return;
        live.setStatus(this.dirty.size
          ? this.dirty.size + ' unsaved change' + (this.dirty.size === 1 ? '' : 's')
          : '');
        const saveBtn = live.el.querySelector('.pm-footer .pm-btn.primary');
        if (saveBtn) saveBtn.disabled = this.dirty.size === 0;
      },
    };

    const tabs = Object.entries(SECTIONS).map(([id, sec]) => ({
      id, label: sec.label,
      content: () => {
        const wrap = h('div');
        sec.groups.forEach(g => wrap.appendChild(renderGroup(g, state, rec)));
        return wrap;
      },
    }));

    const headerTitle = h('span', null, 'Staging · ',
      h('span', { style: { color: 'var(--pm-accent)' } },
        rec.context.address || rec.values.Staging_Display_Name || '(no address)'));
    const subParts = [];
    if (rec.context.staging_date)
      subParts.push(rec.context.staging_date + (rec.context.staging_eta ? ' ' + rec.context.staging_eta : ''));
    if (rec.context.team) subParts.push(rec.context.team);
    if (rec.context.status) subParts.push(rec.context.status);

    const modal = Portal.Modal.open({
      id: 'staging-edit-' + stagingId,
      title: headerTitle,
      subtitle: subParts.join(' · '),
      size: 'lg',
      tabs,
      footer: [
        { label: 'Cancel', onClick: ({ close }) => {
          if (state.dirty.size && !confirm('Discard unsaved changes?')) return;
          close();
        }},
        { label: 'Save', kind: 'primary', disabled: true, onClick: async ({ close }) => {
          if (state.dirty.size === 0) return;
          const patch = {};
          state.dirty.forEach(k => patch[k] = state.values[k]);
          modalRef.value.busy(true);
          try {
            const r = await fetch('/portal/staging/' + encodeURIComponent(stagingId) + '/save', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ patch }),
            });
            const j = await r.json();
            if (!r.ok || j.error) throw new Error(j.error || ('HTTP ' + r.status));
            modalRef.value.busy(false);
            Portal.Modal.toast('Saved (' + state.dirty.size + ' field'
              + (state.dirty.size === 1 ? '' : 's') + ')', 'success');
            state.dirty.clear();
            modalRef.value.setStatus('');
            if (typeof opts.onSaved === 'function') opts.onSaved(j);
            close();
          } catch (e) {
            modalRef.value.busy(false);
            Portal.Modal.toast('Save failed: ' + e.message, 'error');
          }
        }},
      ],
    });
    modalRef.value = modal;
  }

  window.StagingEditModal = { open: openModal, _sections: SECTIONS };
})();
