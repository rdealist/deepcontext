# DeepContext UI Design Specification

## Overview
This document outlines the visual design system for DeepContext, inspired by a natural "Plant Care" aesthetic. The design emphasizes cleanliness, organic tones, and clarity.

## 1. Typography
We use a pairing of a quirkier, geometric sans-serif for headings and a clean, legible sans-serif for body text.

### Primary Fonts
- **Headings**: `Space Grotesk` (Google Fonts)
  - Usage: `h1`, `h2`, `h3`, `h4`, landing page titles.
  - Variable: `--font-heading`
- **Body**: `Noto Sans` (Google Fonts)
  - Usage: Paragraphs, UI elements, data tables.
  - Variable: `--font-sans`

## 2. Color Palette
The color system is built on Warm Greys (Stone) and Vibrant Greens.

### Semantic Colors
| Token | Tailwind Class | Hex | Description |
|-------|----------------|-----|-------------|
| **Background** | `bg-background` (Stone-50) | `#fafaf9` | Main app background. |
| **Foreground** | `text-foreground` (Stone-900) | `#1c1917` | Primary text. |
| **Primary** | `bg-primary` (Green-500) | `#22c55e` | Main actions, active states. |
| **Secondary** | `bg-secondary` (Stone-100) | `#f5f5f4` | Secondary buttons, backgrounds. |
| **Card** | `bg-card` (White) | `#ffffff` | Component backgrounds. |
| **Muted** | `text-muted-foreground` (Stone-500) | `#78716c` | Secondary text, captions. |
| **Border** | `border-border` (Stone-200) | `#e7e5e4` | Dividers, borders. |

### Usage Rules
- **Backgrounds**: Use `bg-background` for the page root. Use `bg-card` for specific content containers.
- **Text**: Use `text-stone-900` for headings and primary content. Use `text-stone-600` or `text-muted-foreground` for metadata.
- **Accents**: Use `text-green-500` or `bg-green-500` sparingly for key interactions or status indicators.

## 3. Component Styles

### Cards
- **Structure**: `bg-white rounded-xl shadow-lg border border-stone-200`
- **Interaction**: Add `hover:shadow-xl transition-all duration-300` for interactive cards.
- **Padding**: Generous padding (`p-4` or `p-6`).

### Buttons
- **Primary**: `bg-green-500 hover:bg-green-600 text-white shadow-sm rounded-lg`.
- **Secondary**: `bg-white hover:bg-stone-50 text-stone-700 border border-stone-300`.
- **Ghost**: `hover:bg-stone-100 text-stone-600`.

### Inputs
- **Base**: `bg-stone-50 border-stone-300 text-stone-900`.
- **Focus**: `focus:ring-2 focus:ring-green-500 focus:border-green-500`.
- **Radius**: `rounded-lg`.

### Tables
- **Header**: `bg-stone-100 text-stone-600 uppercase text-xs font-medium`.
- **Rows**: `border-b border-stone-200 hover:bg-stone-50`.

## 4. Icons
- Use **Lucide React** (default) or **Material Icons** (if specific match needed).
- Style: `stroke-width={1.5}` or `2` for clarity.
- Color: Usually `text-stone-500` or `text-green-500`.

## 5. Layout
- **Containers**: `max-w-5xl mx-auto` for main content areas.
- **Spacing**: Use multiples of 4 (e.g., `gap-4`, `py-8`).
- **Glassmorphism**: Use `.glass` utility for overlay elements (`backdrop-blur-xl bg-white/80`).
