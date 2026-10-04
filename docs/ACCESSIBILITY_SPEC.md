# Accessibility & Inclusive Design Specification
## ShopStream-Copilot WCAG 2.1 AA Compliance Standard
**Team:** YouTube Accessibility & Consumer Growth Team (Zurich)  
**Document ID:** ACC-2026-YTS-001  

---

## 1. Overview & Core Principles

The ShopStream-Copilot UI surface is engineered to satisfy **WCAG 2.1 Level AA** standards. In-stream video shopping must never obstruct primary video playback, closed captions, or screen reader navigation for viewers with visual, motor, or cognitive impairments.

---

## 2. Key Accessibility Standards & Features

### 2.1 Screen Reader Live Region Integration (`aria-live`)
- **Polite Announcements (`aria-live="polite"`):** When the ShopStream-Copilot drawer updates with newly featured products as the video playback timestamp advances, screen readers receive polite announcements without interrupting current video narration.
- **Urgent Announcements (`aria-live="assertive"`):** When a 1-Click Google Pay order confirmation is completed, screen readers announce the order transaction ID and summary immediately.

```html
<div id="shopstream-live-announcer" aria-live="polite" aria-atomic="true" class="sr-only">
  Featured Product updated: Sony FE 24-70mm f/2.8 GM II Lens, Price $2,298.00 USD.
</div>
```

### 2.2 Non-Blocking Closed Caption (CC) Overlay Layout
- The ShopStream drawer is positioned in the lower-right quadrant on desktop and collapsible bottom sheet on mobile, strictly preserving the standard lower-center area reserved for YouTube Closed Captions (CC) and Subtitles.

### 2.3 WCAG High Contrast Theme Specification
- **Normal Mode:** Minimum contrast ratio 4.5:1 for standard text (#F1F1F1 text on #212121 dark card background).
- **High Contrast Mode:** Pure black (#000000) background with high contrast yellow (#FFFF00) active element borders and pure white (#FFFFFF) bold text (contrast ratio > 15:1).

### 2.4 Tactile Keyboard Navigation & Focus Management
- **Focus Rings:** High-visibility 3px solid accent focus rings around all interactive buttons and inputs.
- **Shortcuts:**
  - `Spacebar`: Toggle Video Play / Pause
  - `Shift + S`: Toggle ShopStream In-Stream Drawer
  - `Shift + C`: Trigger UCP 1-Click Checkout on primary product
  - `Alt + A`: Trigger screen reader audio readout of active transcript cue
