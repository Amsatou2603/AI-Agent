---
name: L'Excellence Numérique
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#3e4a41'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#6e7a70'
  outline-variant: '#bdcabe'
  surface-tint: '#006d40'
  primary: '#006b3f'
  on-primary: '#ffffff'
  primary-container: '#008751'
  on-primary-container: '#fdfff9'
  inverse-primary: '#70db9d'
  secondary: '#715d00'
  on-secondary: '#ffffff'
  secondary-container: '#fed41b'
  on-secondary-container: '#705b00'
  tertiary: '#bd0014'
  on-tertiary: '#ffffff'
  tertiary-container: '#e61e25'
  on-tertiary-container: '#fffdff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#8df8b7'
  primary-fixed-dim: '#70db9d'
  on-primary-fixed: '#002110'
  on-primary-fixed-variant: '#00522f'
  secondary-fixed: '#ffe178'
  secondary-fixed-dim: '#ebc300'
  on-secondary-fixed: '#231b00'
  on-secondary-fixed-variant: '#554500'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb4ac'
  on-tertiary-fixed: '#410002'
  on-tertiary-fixed-variant: '#93000d'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-margin: 20px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
  stack-xl: 40px
---

## Brand & Style
This design system embodies the intersection of Senegalese national pride and cutting-edge artificial intelligence. The aesthetic is defined as **Premium Glassmorphism**, prioritizing clarity, authority, and technological sophistication. 

The personality is "The Informed Diplomat"—professional, trustworthy, and visionary. It avoids the flat, utilitarian look of traditional government portals in favor of a layered, high-fidelity interface that suggests transparency and intelligence. The emotional goal is to make the user feel empowered by data while maintaining a sense of national identity through a refined color application.

## Colors
The palette elevates the national colors of Senegal into a professional domain. 
- **Deep Emerald (#008751):** Used for primary actions, header backgrounds, and brand signifiers. It represents growth and stability.
- **Sun-Kissed Gold (#FBD116):** Used sparingly as an accent for focus states, star ratings, or high-value data highlights.
- **Soft Crimson (#E31B23):** Reserved for critical alerts, error states, or subtle semantic highlights, ensuring it doesn't overwhelm the calm aesthetic.
- **Premium Neutrals:** The background uses a crisp off-white (#F8F9FA) to ensure the "glass" elements have enough contrast to appear translucent.

## Typography
**Inter** is selected for its systematic, neutral, and highly legible characteristics. 
- **Headlines:** Use tighter letter-spacing and heavier weights to project authority. 
- **Body Text:** Maintains generous line-height for readability during long AI-generated responses.
- **Labels:** Use Medium weight to distinguish metadata from body content.
- **Mobile Scaling:** For mobile devices, `display-lg` should be capped at 32px to prevent awkward text wrapping.

## Layout & Spacing
This design system utilizes a **fluid grid** optimized for mobile-first interaction. 
- **Margins:** A standard 20px safe area on horizontal edges.
- **Vertical Rhythm:** Built on an 8px base unit. Components are separated by 16px (md) or 24px (lg) increments to maintain a "breathable" premium feel.
- **AI Chat Layout:** User messages are right-aligned with solid backgrounds; AI responses are left-aligned using the glassmorphic surface treatment to indicate they are "generated" and distinct.

## Elevation & Depth
Depth is created through a combination of **Backdrop Blurs** and **Ambient Shadows**.
- **Level 1 (Base):** Flat background color (#F8F9FA).
- **Level 2 (Cards):** Glassmorphic surfaces with a 12px backdrop blur, 70% white opacity, and a 1px white inner border to simulate a glass edge.
- **Level 3 (Floating Actions):** Soft, diffused shadows using a tint of the primary color (e.g., `rgba(0, 135, 81, 0.08)`) with a 20px blur radius.
- **Level 4 (Modals/Overlays):** High-contrast glass with 20px blur and a subtle dimming of the background layer.

## Shapes
Shapes are intentionally friendly yet structured. 
- **Standard Corners:** 16px (rounded) for secondary cards and inputs.
- **Large Containers:** 24px (rounded-lg) for main content blocks and persistent bottom sheets.
- **Interactive Elements:** Buttons and tags utilize a semi-pill shape (rounded-xl) to feel "squishy" and modern.

## Components
- **Primary Buttons:** High-contrast Emerald (#008751) with white text. Use a subtle gradient (top-to-bottom) for a tactile feel.
- **Glass Cards:** The signature component. Transparent white background with a 1px `glass_border`. Used for AI responses and dashboard stats.
- **Input Fields:** Sleek, 16px rounded borders. On focus, the border transitions to a 2px Emerald stroke with a soft outer glow.
- **Chips/Filters:** Pill-shaped with a light Emerald tint (10% opacity) and 500 weight text for active states.
- **Progress Indicators:** Use the Gold (#FBD116) for loading states and progress bars to suggest "intelligence at work."
- **Status Badges:** Small, uppercase labels with background colors reflecting the Flag palette (Green for active, Yellow for pending, Red for restricted).