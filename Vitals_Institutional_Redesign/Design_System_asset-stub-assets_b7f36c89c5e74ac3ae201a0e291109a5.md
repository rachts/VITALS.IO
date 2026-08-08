---
name: Vitals Institutional
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#201f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#d0c5b5'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#998f81'
  outline-variant: '#4d463a'
  surface-tint: '#e4c285'
  primary: '#e6c487'
  on-primary: '#412d00'
  primary-container: '#c9a96e'
  on-primary-container: '#543d0c'
  inverse-primary: '#745a27'
  secondary: '#b9ccb0'
  on-secondary: '#253421'
  secondary-container: '#3d4d38'
  on-secondary-container: '#abbea2'
  tertiary: '#ffb6b4'
  on-tertiary: '#620f16'
  tertiary-container: '#ff8c8a'
  on-tertiary-container: '#792125'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdea4'
  primary-fixed-dim: '#e4c285'
  on-primary-fixed: '#261900'
  on-primary-fixed-variant: '#5a4312'
  secondary-fixed: '#d5e8cb'
  secondary-fixed-dim: '#b9ccb0'
  on-secondary-fixed: '#101f0d'
  on-secondary-fixed-variant: '#3b4b36'
  tertiary-fixed: '#ffdad8'
  tertiary-fixed-dim: '#ffb3b0'
  on-tertiary-fixed: '#410007'
  on-tertiary-fixed-variant: '#81262a'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 64px
    fontWeight: '500'
    lineHeight: 72px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 40px
    fontWeight: '500'
    lineHeight: 48px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Manrope
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Manrope
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.08em
  data-mono:
    fontFamily: Courier Prime
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1440px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style
The design system is anchored in an institutional, editorial aesthetic that balances the authority of legacy finance with the precision of modern high-end software. The brand personality is sophisticated, restrained, and deeply trustworthy, evoking the feel of a boutique hedge fund or a premium private bank.

The visual style follows a **Modern Editorial** movement:
- **Solid Layering:** Surfaces are opaque and structured, avoiding the trendiness of glassmorphism in favor of "physical" permanence.
- **Grain & Texture:** A subtle global noise overlay (2-3% opacity) is applied to all surfaces to eliminate sterile digital banding and provide a paper-like tactile quality.
- **Asymmetry:** Layouts prioritize editorial white space and intentional imbalances to guide the eye toward critical financial data.
- **Restraint:** No neon glows or aggressive gradients. Distinction is achieved through high-contrast typography and desaturated, noble metal accents.

## Colors
The palette is rooted in "Warm Noir"—a deep, charcoal-black base with organic warmth. 

- **Primary Gold (#C9A96E):** Used sparingly for primary actions and key status indicators. It is desaturated to maintain an institutional feel.
- **Sage Secondary (#8B9D83):** Employed for positive fiscal trends and success states, providing a calm alternative to standard neon greens.
- **Text Hierarchy:** Contrast is carefully managed. Primary information uses a warm white (#F0EFEA) to reduce eye strain, while secondary data is suppressed in warm gray.
- **Light Mode:** Reserved for "Economics" or "Report" views, switching to a high-readability off-white (#F5F3EF) background that mimics premium financial broadsheets.

## Typography
The typography system uses a sharp contrast between **Playfair Display** (Serif) and **Manrope** (Sans-Serif).

- **Editorial Serifs:** Headlines must use Playfair Display with weights between 500 and 600. Large display sizes should use slight negative letter spacing to create a dense, authoritative "newspaper" feel.
- **Institutional Sans:** All UI elements, body copy, and data inputs use Manrope. Its geometric clarity ensures that dense financial tables remain legible.
- **Labels:** Small labels and metadata should always be uppercase with an expanded letter-spacing of 0.08em to evoke architectural blueprints or luxury branding.
- **Data Tables:** For high-density financial grids, use a monospaced font (Courier Prime) for numerals to ensure columnar alignment.

## Layout & Spacing
The layout system follows a **12-column fixed grid** for desktop and a **4-column fluid grid** for mobile.

- **Editorial Rhythm:** Use generous, asymmetrical margins. Significant sections should be separated by "xl" (80px) spacing to allow the content to breathe.
- **Grid Alignment:** Align text-heavy components to the center 8 columns, leaving the outer columns for auxiliary navigation or decorative data points.
- **Density:** Financial dashboards use a 16px gutter (sm) to maximize information density, while marketing or landing pages use 48px (lg) gutters to emphasize the premium feel.

## Elevation & Depth
Depth is created through **Tonal Layering** rather than shadows. 

- **Surface Levels:** The base background is #0C0C0E. Cards and containers sit on #141416. Input fields and active states sit on #1A1A1C.
- **Shadows:** When shadows are necessary for modals or menus, they must be extremely diffused and large (40px-60px blur). The shadow color must be a dark umber or deep navy—never pure black—to maintain the warmth of the palette.
- **Dividers:** Use hairline borders (1px) with low opacity (rgba 240, 239, 234, 0.08). Avoid heavy borders unless defining a primary dashboard region.

## Shapes
The design system utilizes **Soft** geometry (0.25rem / 4px base radius).

- **Precision:** Corners are kept tight to reflect precision and institutional reliability. 
- **Interactive Elements:** Buttons and input fields use the standard 4px radius. Large card containers may scale up to 8px (rounded-lg) but never exceed this to avoid a "bubbly" or consumer-grade appearance.
- **Pills:** Forbidden for buttons, but acceptable for small status tags (e.g., "Active") to provide a visual break from the rigid grid.

## Components
- **Buttons:** Primary buttons use a solid Gold (#C9A96E) background with near-black text. Secondary buttons use a ghost style: 1px border of #F0EFEA at 10% opacity, transitioning to 20% on hover.
- **Input Fields:** Background set to #1A1A1C with a subtle 1px bottom-border only. Labels sit above the field in `label-caps` style.
- **Cards:** Cards should not have shadows by default. They are defined by their #141416 surface and a very faint `border_card` outline.
- **Status Indicators:** Use the desaturated Sage for success and Brick Red for critical alerts. Indicators should be small, solid circles or 1px stroke icons.
- **Motion:** Transitions should be linear-out or standard-easing (cubic-bezier(0.4, 0, 0.2, 1)). Duration should be 200ms-300ms. No "pop" or "spring" effects; the UI should feel heavy and mechanical.
- **Data Visualizations:** Charts use the Primary Gold and Sage colors. Use thin line weights (1.5px) and avoid filled area charts unless the opacity is below 10%.