# CompilerX — UI/UX Design System & Developer Guidelines
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Frontend Design System |
| **Author** | Principal Software Architect & Technical Lead |
| **Design Direction** | Dark-First Developer Platform (Linear / Vercel / Raycast Aesthetic) |
| **Typography** | `Inter` (UI Prose) + `JetBrains Mono` / `Fira Code` (Code & Numbers) |
| **Grid & Spacing** | Strict 4px/8px Base Grid System |
| **Last Updated** | 2026-11-06 |

---

## 1. Design Philosophy & Aesthetic Direction

CompilerX is an engineering platform built for programmers, researchers, and systems engineers. The user interface must project technical competence, precision, speed, and restraint.

### 1.1 Core Aesthetic Principles
1. **Dark-First Native Environment:** Built from the ground up for dark mode. Reduces eye strain during extended coding and telemetry review sessions.
2. **High Information Density with Visual Breathing Room:** Dense, tabular, and metric-rich information layouts organized with strict alignment, subtle dividers, and consistent padding.
3. **Restrained Color as Functional Semantic Indicator:** Color is reserved strictly for semantic state (compilation success, syntax error, performance regression, ML confidence). Backgrounds and structural frames remain strictly neutral.
4. **Zero Aesthetic Gimmicks (Anti-Patterns Prohibited):**
   - **NO** excessive background gradients or psychedelic glows.
   - **NO** random glassmorphism / heavy backdrop blur that reduces text legibility.
   - **NO** oversized, bubbly cards with low data-to-pixel ratios.
   - **NO** playful or slow animations ($> 200\text{ms}$) that delay productivity.
   - **NO** fabricated charts or decorative animated counters.

---

## 2. Color Palette & Semantic System

The color palette is built using Tailwind CSS neutral slates paired with precise semantic indicators:

```
┌────────────────────────────────────────────────────────────────────────┐
│                              BACKGROUNDS                               │
│  Base Canvas (#090D16)   Card/Surface (#0F172A)   Elevated (#1E293B)   │
├────────────────────────────────────────────────────────────────────────┤
│                                BORDERS                                 │
│  Subtle Frame (#1E293B)  Interactive Border (#334155) Active (#64748B)│
├────────────────────────────────────────────────────────────────────────┤
│                           SEMANTIC ACCENTS                             │
│  Primary (Cyan #06B6D4)  Success (Emerald #10B981)                     │
│  Warning (Amber #F59E0B) Danger (Rose #F43F5E)                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Detailed Color Specification Table

| Token Name | Hex Code | Tailwind Equivalent | Functional Role |
|---|---|---|---|
| `bg-canvas` | `#090d16` | `slate-950` (custom) | Deepest application background, page base. |
| `bg-surface` | `#0f172a` | `slate-900` | Card containers, sidebar panels, editor frame. |
| `bg-elevated`| `#1e293b` | `slate-800` | Modals, dropdown popovers, active tabs. |
| `border-subtle` | `#1e293b`| `slate-800` | Structural panel dividers and table rows. |
| `border-focus`| `#334155` | `slate-700` | Hover states, active input borders. |
| `text-primary`| `#f8fafc` | `slate-50` | Primary headings, code, active labels. |
| `text-secondary`| `#94a3b8`| `slate-400` | Metadata labels, descriptions, timestamps. |
| `text-muted` | `#64748b` | `slate-500` | Disabled elements, placeholder text. |
| `accent-primary`| `#06b6d4`| `cyan-500` | Active selection, primary CTA, ML badges. |
| `state-success`| `#10b981` | `emerald-500` | Clean compilation (exit code 0), speedup $>1.0\times$. |
| `state-warning`| `#f59e0b` | `amber-500` | Compiler warnings, high-variance runs ($CV > 15\%$). |
| `state-danger` | `#f43f5e` | `rose-500` | Compilation errors, syntax faults, timeouts. |

---

## 3. Typography & Hierarchy

### 3.1 Font Stacks
- **UI Interface Font:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `sans-serif`.
  - Chosen for tall x-height, clear optical kerning, and crisp legibility at small sizes ($11\text{px} \dots 14\text{px}$).
- **Monospace & Numeric Font:** `JetBrains Mono`, `Fira Code`, `"Menlo"`, `"Monaco"`, `monospace`.
  - Configured with tabular numbers (`font-variant-numeric: tabular-nums`) so benchmark columns align vertically without jitter.

### 3.2 Type Scale

| Element | Size | Weight | Line Height | Tracking | Font Stack |
|---|---|---|---|---|---|
| **App Title** | `18px` (`text-lg`) | Bold (700) | `24px` | `-0.02em` | Inter |
| **Section Header**| `14px` (`text-sm`) | Semi-Bold (600) | `20px` | `-0.01em` | Inter |
| **Panel Label** | `12px` (`text-xs`) | Medium (500) | `16px` | `+0.02em` (caps) | Inter |
| **Prose / Body** | `13px` | Regular (400) | `18px` | `normal` | Inter |
| **Editor Code** | `13px` | Regular (400) | `20px` | `normal` | JetBrains Mono |
| **Metric Value** | `20px` (`text-xl`)| Bold (700) | `24px` | `-0.03em` | JetBrains Mono |
| **Table Data** | `12px` (`text-xs`) | Regular (400) | `16px` | `normal` | JetBrains Mono |

---

## 4. Information Architecture & Workspace Layout

The primary workspace (`/projects/:id`) utilizes a **three-column responsive grid** maximizing developer focus:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ [Logo] CompilerX  |  Project: Matrix Multiply  |  [Lang: C]    [Status: Ready] [Help] │
├──────────────┬────────────────────────────────────────────┬───────────────────────────┤
│ FILE TREE    │ SOURCE CODE WORKBENCH (Monaco Editor)      │ COMPILER & BENCHMARK      │
│ (220px)      │ (Flexible: min 450px)                      │ INSPECTOR (380px)         │
│              │                                            │                           │
│ 📁 src       │ 1  #include <stdio.h>                      │ [Optimization Level]      │
│   📄 main.c  │ 2  #define N 512                           │ ( -O0 ) ( -O1 ) ( -O2 )   │
│   📄 utils.c │ 3                                          │ [★ -O3 (Recommended)]    │
│              │ 4  int main() {                            │                           │
│ 📄 Readme.md │ 5      double A[N][N];                     │ [Auxiliary Flags]         │
│              │ 6      // Matrix multiplication loop       │ [x] -Wall  [x] -ffast-math│
│ [+ New File] │ 7      for(int i=0; i<N; i++) {            │                           │
│              │ 8          for(int j=0; j<N; j++) {        │ [ Compile ]  [ Run Suite ]│
│              │ 9              ...                         │ ───────────────────────── │
│              │                                            │ ML RECOMMENDATION         │
│              │                                            │ Badge: -O3 (Conf: 88%)    │
│              │                                            │ Rationale: High nesting.  │
├──────────────┴────────────────────────────────────────────┴───────────────────────────┤
│ COLLAPSIBLE DRAWER: [ >_ Compiler Terminal (Clang Diagnostics) ]  [ 📊 Live Analytics ]│
│ Status: Clang-17 exited with code 0. Binary size: 22,416 bytes. Compilation time: 142ms│
└───────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Component Sizing & Proportions
- **Left Sidebar (File Tree):** Fixed $220\text{px}$ width. Collapsible via `Cmd+B` shortcut.
- **Center Canvas (Monaco Editor):** Fluid flex-grow width. Minimum width constraint of $450\text{px}$.
- **Right Inspector (Controls & Benchmark KPIs):** Fixed $380\text{px}$ width. Houses level toggles, recommendation card, and summary metrics.
- **Bottom Drawer (Terminal / Analytics):** Collapsible panel ($180\text{px}$ default height) toggling between raw compiler terminal output and real-time Recharts performance graphs.

---

## 5. Visual Analytics & Chart Design Guidelines

All charts are implemented using **Recharts** and styled to integrate seamlessly into the dark palette:

### 5.1 Palette & Styling
- **Background:** Transparent (charts sit directly on `bg-surface`).
- **Grid Lines:** `stroke="#1e293b"` (subtle dashed grid lines, `strokeDasharray="3 3"`).
- **Axis Labels:** `fill="#94a3b8"`, `fontSize=11`, `fontFamily="JetBrains Mono"`.
- **Bar Series Colors:**
  - `-O0` (Baseline): `#64748b` (Neutral Slate)
  - `-O1`: `#38bdf8` (Light Sky Blue)
  - `-O2`: `#818cf8` (Indigo)
  - `-O3`: `#06b6d4` (Vibrant Cyan)
  - *Recommended Level Indicator:* Glowing border or star glyph on top of the bar.

### 5.2 Tooltip Design
Custom tooltips must format numbers cleanly:
```tsx
<div className="bg-slate-800 border border-slate-700 p-2.5 rounded shadow-xl text-xs font-mono">
  <div className="text-slate-400 font-semibold mb-1">{label}</div>
  <div className="text-cyan-400">Mean: {payload.mean_ms.toFixed(2)} ms</div>
  <div className="text-slate-300">StdDev: ±{payload.stddev_ms.toFixed(2)} ms</div>
  <div className="text-emerald-400 font-bold">Speedup: {payload.speedup}x</div>
</div>
```

---

## 6. Micro-Interactions & Keyboard Accessibility

### 6.1 State Transitions
- **Button Hover / Active:** `transition-all duration-150 ease-out`. Buttons scale slightly down on active press (`active:scale-[0.98]`).
- **Terminal Feed:** New log lines fade in with a $100\text{ms}$ entry opacity transition.
- **Tab Switching:** Instant layout swap with zero cross-fade lag.

### 6.2 Universal Keyboard Shortcuts

| Shortcut | Action | Scope |
|---|---|---|
| `Cmd+S` / `Ctrl+S` | Save active file buffer to backend | Code Editor |
| `Cmd+Enter` / `Ctrl+Enter` | Trigger compilation with active flags | Global Workspace |
| `Cmd+Shift+B` | Trigger full benchmark suite run | Global Workspace |
| `Cmd+B` | Toggle left file-tree sidebar | Global Workspace |
| `Esc` | Dismiss modals, close drawers | Global Modals |

---

*This document establishes the official UI/UX design guidelines for CompilerX.*

