---
name: Academic Governance
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#44474e'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#495f82'
  primary: '#001026'
  on-primary: '#ffffff'
  primary-container: '#0b2545'
  on-primary-container: '#778db2'
  inverse-primary: '#b1c7f0'
  secondary: '#385ca6'
  on-secondary: '#ffffff'
  secondary-container: '#8eafff'
  on-secondary-container: '#164089'
  tertiary: '#031122'
  on-tertiary: '#ffffff'
  tertiary-container: '#182638'
  on-tertiary-container: '#7f8da3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#b1c7f0'
  on-primary-fixed: '#001c3b'
  on-primary-fixed-variant: '#314769'
  secondary-fixed: '#d9e2ff'
  secondary-fixed-dim: '#b0c6ff'
  on-secondary-fixed: '#001944'
  on-secondary-fixed-variant: '#1b448d'
  tertiary-fixed: '#d5e3fc'
  tertiary-fixed-dim: '#b9c7df'
  on-tertiary-fixed: '#0d1c2e'
  on-tertiary-fixed-variant: '#3a485b'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
  data-metric:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
  data-tabular:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  gutter-lg: 2rem
  margin: 1.5rem
  margin-mobile: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system establishes an authoritative, precise, and transparent visual language for university administration and personnel monitoring. Built specifically for higher education governance and public institutional workflows, the interface balances institutional gravitas with the frictionless utility of modern enterprise software.

### Tone & Character
- **Institutional Authority:** Grounded in deep academic navy and deliberate structural alignment. It conveys accountability, integrity, and administrative permanence.
- **Clarity & Decisiveness:** Eliminates cognitive overhead for deans, department heads, and HR officers reviewing bulk submissions through stark hierarchy and immediate visual triage.
- **Calm Utility:** Clean white and light slate canvases prevent visual exhaustion during long administrative shifts and data reconciliation tasks.

### Design Movement
- **Corporate / Modern Institutional:** Crisp neutral backgrounds, structured borders, and subtle elevation tiers create a high-trust administrative workspace. Skeuomorphism and decorative gradients are discarded in favor of sharp typographic order, high data density, and clear status communication.

## Colors

The color palette centers on trusted naval blues anchored by a functional slate scale and a high-visibility semantic status tier. Contrast ratios strictly satisfy WCAG 2.1 AA standards for institutional accessibility.

### Primary & Brand Scales
- **Primary Navy (`#0B2545`):** The institutional anchor, applied to top-level navigation headers, primary buttons, active structural navigation, and high-level KPI metric values.
- **Secondary Royal Navy (`#133E87`):** Interactive accents, active focus rings, active tab indicators, and secondary administrative CTAs.
- **Slate Steel Neutral (`#475569`):** Subdued structural elements, secondary body copy, table headers, and inactive states.

### Semantic Status System (Status & Verification Lifecycle)
- **Approved / Complete (Disetujui / Selesai):** Text/Icon: `#16A34A`, Fill: `#DCFCE7`, Border: `#86EFAC`.
- **Pending / In Transit (Menunggu Persetujuan / Sedang di Luar):** Text/Icon: `#D97706`, Fill: `#FEF3C7`, Border: `#FCD34D`.
- **Violations / Rejected / Overdue (Terlambat Kembali / Ditolak):** Text/Icon: `#DC2626`, Fill: `#FEE2E2`, Border: `#FCA5A5`.
- **Archived / Cancelled (Dibatalkan / Arsip):** Text/Icon: `#64748B`, Fill: `#F1F5F9`, Border: `#CBD5E1`.

### Surface & Border Rules
- **Base Canvas:** `#F8FAFC` provides a calm backdrop that separates application panels from the viewport frame.
- **Card / Surface Container:** Pure `#FFFFFF` ensures maximal contrast for data tables and metrics.
- **Dividers & Strokes:** `#E2E8F0` defines tabular grids and card perimeters without high visual friction.

## Typography

The typographic hierarchy pairs **Plus Jakarta Sans** for display structures, page headers, and KPI numerals with **Inter** for data density, tables, and functional body copy.

### Typographic Rules & Usage
- **Tabular Figures:** All data tables, timestamps, NIP (Nomor Induk Pegawai) codes, durations, and KPI totals must enforce OpenType tabular figures (`font-variant-numeric: tabular-nums;`) to guarantee strict vertical alignment across comparative rows.
- **Letter Spacing:** All uppercase administrative labels (`label-sm`) require `letter-spacing: 0.05em` to preserve legibility in dense audit tables and status tags.
- **Hierarchy Enforcers:**
  - `data-metric`: Used strictly inside KPI cards for aggregate counts.
  - `data-tabular`: Standardized for table cells, balancing dense multi-row rendering with quick scannability.

## Layout & Spacing

The layout employs an enterprise-grade 12-column fluid grid system engineered to accommodate high-density data views, side-by-side verification panels, and audit sidebars.

### Grid Architecture & Breakpoints
- **Desktop (≥ 1280px):** 12 columns, `margin-desktop` (2rem / 32px), `gutter` (1.5rem / 24px). Primary layout features a persistent 260px administrative navigation sidebar alongside the flexible main application canvas.
- **Tablet (768px – 1279px):** 8 columns, `margin` (1.5rem / 24px), `gutter-sm` (1rem / 16px). Navigation collapses to an icon-rail or off-canvas drawer. Data filter clusters wrap into collapsible disclosure panels.
- **Mobile (< 768px):** 4 columns, `margin-mobile` (1rem / 16px), `gutter-sm` (1rem / 16px). KPI metrics stack horizontally inside touch-swipable containers; data tables convert to stacked status cards.

### Spacing Principles
- Component internal padding strictly references the `space-*` scale.
- Interactive fields (inputs, buttons) utilize `space-sm` vertical padding and `space-md` horizontal padding to maintain institutional touch targets without consuming excessive screen real estate.

## Elevation & Depth

To sustain an administrative and institutional aesthetic, depth is established through **subtle structural borders combined with soft, low-amplitude ambient shadows**. High blur distances and deep black shadows are avoided to keep tabular data legible.

### Elevation Levels
- **Level 0 (Flat / Canvas):** Surface color `#F8FAFC`, 0px shadow. Used for backdrops and layout wrappers.
- **Level 1 (Card & Table Surface):** Background `#FFFFFF`, border `1px solid #E2E8F0`, shadow `0 1px 3px 0 rgba(11, 37, 69, 0.04), 0 1px 2px -1px rgba(11, 37, 69, 0.02)`. Standard for KPI metrics, data tables, and structured panels.
- **Level 2 (Popovers, Flyouts, Menus):** Background `#FFFFFF`, border `1px solid #CBD5E1`, shadow `0 4px 6px -1px rgba(11, 37, 69, 0.08), 0 2px 4px -2px rgba(11, 37, 69, 0.04)`. Applied to filter menus, export dropdowns, and date pickers.
- **Level 3 (Modal Dialogs & Approval Panels):** Background `#FFFFFF`, border `1px solid #CBD5E1`, shadow `0 20px 25px -5px rgba(11, 37, 69, 0.12), 0 8px 10px -6px rgba(11, 37, 69, 0.04)`. Accompanied by a 40% opacity backdrop overlay (`rgba(11, 37, 69, 0.40)` with `backdrop-filter: blur(2px)`).

## Shapes

The shape system adopts a **Soft (`1`)** geometry. Crisp, conservative edge radii communicate structural reliability and governmental authority without feeling dated.

### Curvature Tokens
- **Standard UI Elements (`0.25rem` / 4px):** Form controls, text inputs, segmented button controls, table row hover highlights, and standard badges.
- **Cards & Data Containers (`rounded-lg` / `0.5rem` / 8px):** KPI metric blocks, audit overview cards, and primary data tables.
- **Modals & Flyout Sheets (`rounded-xl` / `0.75rem` / 12px):** Verification dialogs, reject reason inputs, and approval detail flyouts.
- **Fully Rounded / Pill (`9999px`):** Reserved exclusively for employee avatars and count indicator badges.

## Components

### Buttons
- **Primary:** Background `#0B2545`, text `#FFFFFF`, border `none`, hover state `#133E87`. Focused with a 2px offset ring in `#133E87`. Used for primary submission and approval actions.
- **Secondary / Outline:** Background `#FFFFFF`, text `#0B2545`, border `1px solid #CBD5E1`, hover state `#F1F5F9`. Used for filters, exports, and navigation actions.
- **Destructive:** Background `#DC2626`, text `#FFFFFF`, hover state `#B91C1C`. Used for rejecting requests or revoking permits.
- **Sizing:** Fixed heights of 36px (compact administrative) and 40px (default), maintaining 4px corner radii.

### Status Badges & Chips
- Status indicators must always present high-contrast pairs (light tint background + dark saturated text) encased in a matching 1px border.
- **Structure:** `padding: 2px 8px`, `border-radius: 4px`, `font-size: 11px`, `font-weight: 600`, text uppercase with 0.05em tracking.
- **Status Configurations:**
  - *Disetujui:* `#DCFCE7` bg, `#16A34A` text, `#86EFAC` border.
  - *Menunggu Persetujuan:* `#FEF3C7` bg, `#D97706` text, `#FCD34D` border.
  - *Sedang di Luar:* `#E0F2FE` bg, `#0284C7` text, `#7DD3FC` border.
  - *Terlambat Kembali:* `#FEE2E2` bg, `#DC2626` text, `#FCA5A5` border.
  - *Dibatalkan / Arsip:* `#F1F5F9` bg, `#64748B` text, `#CBD5E1` border.

### Executive KPI Stat Cards
- Container styled with Level 1 elevation, `#FFFFFF` background, 1px `#E2E8F0` border, and 8px border radius.
- Padding set to `1.25rem` (20px).
- Internal layout displays the category label (`label-md` in `#475569`) at the top, a prominent count (`data-metric` in `#0B2545`) in the center, and a contextual footer displaying daily delta or percentage with status color coding.

### Modern Institutional Data Tables
- **Header:** `#F8FAFC` background, height 40px, border-bottom `1px solid #CBD5E1`. Typography uses `label-sm` in `#475569`, uppercase, with left alignment for text and right alignment for counts/actions.
- **Rows:** Height 52px, alternating or clean white rows with `1px solid #E2E8F0` dividers. Hover state shifts background to `#F8FAFC`.
- **Columns:** Standardized alignment: Pegawai (Avatar + Name + NIP), Unit Kerja / Fakultas, Jenis Izin, Waktu Keluar / Kembali, Status Badge, Aksi Cepat (Quick Approve/Reject action triggers).

### Input Fields & Select Controls
- Background `#FFFFFF`, border `1px solid #CBD5E1`, corner radius `4px`, height `38px`, text `14px` (`#0F172A`).
- Active focus state uses border color `#133E87` and an outline ring `0 0 0 3px rgba(19, 62, 135, 0.15)`.
- Helper text and error messages render in `12px` font, using `#475569` for defaults and `#DC2626` for validation errors.

### Checkboxes & Radio Controls
- Base dimension `16px × 16px`, border `1px solid #94A3B8`, border-radius `3px` (checkbox) or `50%` (radio).
- Checked state fills with `#0B2545` and renders a pure white icon mark.