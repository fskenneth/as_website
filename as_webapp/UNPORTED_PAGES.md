# Unported Zoho pages — backlog

The Staging Task Board at `/staging_task_board` links into many Zoho Creator
sub-pages that haven't been ported yet. Every button that used to navigate
to one of these now goes to `/stub?page=<name>&...params` and shows a
placeholder. This file is the queue.

Each entry: page name, purpose, typical URL params, known callers (which
button on which column triggers it), priority guess.

| # | Page | Purpose | Params | Called from | Priority |
|---|------|---------|--------|-------------|----------|
| 1 | **Staging_Design** | Per-staging visual layout / design board (3D designer) | `staging_id` | "Design" link on Staging column | **High** — referenced 175x in Task Board |
| 2 | **Staging_Videos_and_Pictures** | Media gallery for a staging (before/after photos, video uploads) | `staging_id` | "Pictures" link on Staging column (conditional on having media) | High |
| 3 | **Packing_Guide_Page** | Furniture-packing checklist for movers | `staging_id`, `staging_type` | "Packing" link on Staging column | High — 147 refs |
| 4 | **Staging_Setup_Guide** | On-site setup instructions for stagers | `staging_id` | "Setup" link on Staging column | High — 136 refs |
| 5 | **Staging_Form** (record-edit) | Full Staging record editor (Zoho-style form for all 150+ fields) | `staging_id`, `Return_Url` | "Edit" link, "Update MLS Info" button, "[New Staging]" header link | High — every row needs edit |
| 6 | **Module_Form** (task edit) | Task / sub-module record editor | `module_id`, `Return_Url` | "[New Task]" header link, per-task "Edit Task" button | High |
| 7 | **Staging_Invoice** | Generated invoice PDF (form-perma on Staging_Invoice in Zoho) | `staging_id`, `Return_Url` | "Download Invoice" button | High — money flow |
| 8 | **Email_Generator** | Compose & send email to customer (Payment Notification, Staging Completion Confirmation, etc.) | `staging_id`, `email_type`, `Return_Url` | "Send Invoice" button + every "Aashika/Nency/Mrunal: send X" task button | High |
| 9 | **Payment_Report** | Payment history view for a staging | `staging_id` | "Payment History" link on Accounting column | Medium |
| 10 | **Daily_Task_Board** | Task-only view (subset of Task Board) | none | Top-bar navigation (menu) | Medium |
| 11 | **Consultation_Report** | Consultation detail/list | none or `consultation_id` | Rendered inline in Task Board; separate drill-in exists | Medium |
| 12 | **Staging_Management** | Alternative staging editor view | `staging_id` | Referenced once | Low |
| 13 | **Astra_Staging_Design** | Customer-facing preview of design | `staging_id` | Referenced once | Low |
| 14 | **Staging_Analytics_Page** | Dashboard / KPIs | none | Menu | Low |
| 15 | **Astra_Staging** | Customer portal home | none | External? | Low (probably public site territory) |
| 16 | **Astra_Staging_Quote** | Customer quote view | `quote_id` | External? | Low (maps to existing `/staging-inquiry/` public flow) |
| 17 | **Unsubscribe_Page** | Email unsubscribe handler | `token` | Email footers | Low |
| 18 | **Task_Pictures_Display_Page** | Task photo gallery | `module_id` | Task row action | Low |
| 19 | **Off_Days_Tracking_Page** | Employee time-off tracking | `employee_id` | HR menu | Low |
| 20 | **Item_Management_Filter_Page** | Inventory filter/search | `filter=...` | Inventory menu | Medium — overlaps with existing `/item_management` sub-app |
| 21 | **Staging_Edit** (internal shorthand) | Record-edit focused on specific field (MLS) | `staging_id`, `focus` | "Update MLS Info" button | Merge with #5 |

## Notes

- **Auth / access**: none for now. When the task board is behind portal auth, sub-pages will inherit.
- **Field updates via URL params**: Zoho's pattern of `?staging_id=X&field_name=Y` → page applies update on load was intentionally skipped. Our port uses HTML form POSTs to `/staging_task_board/set_date` (and will grow similar POST handlers per sub-page when they're built).
- **Field-update whitelist** lives in `staging_task_board.py` as `_DATE_FIELDS`. Extend it when new date-toggle buttons land on other pages.
- When a sub-page is ported, replace its `/stub?page=X` link in the row renderers with the real route.
