================================================================================
THROVE DESIGN SYSTEM & COMPONENT LIBRARY
================================================================================

Version: 1.0
Purpose: Standardized components and patterns for consistent UI
For: UI/UX Designer + Flutter Development Team

================================================================================
1. TYPOGRAPHY SYSTEM
================================================================================

FONT FAMILY:
- Primary: San Francisco Pro (iOS), Roboto (Android)
- Fallback: -apple-system, system-ui, sans-serif
- Used for: Headlines, body text, buttons, labels

FONT SIZES & WEIGHTS:

Display (32px):
- Font Size: 32px
- Font Weight: Bold (700)
- Line Height: 1.2 (38px)
- Usage: Main headings (Dashboard title)
- Color: #1F2937

Heading 1 (24px):
- Font Size: 24px
- Font Weight: Bold (700)
- Line Height: 1.2 (29px)
- Usage: Screen titles, section headings
- Color: #1F2937

Heading 2 (20px):
- Font Size: 20px
- Font Weight: Semi-bold (600)
- Line Height: 1.3 (26px)
- Usage: Card titles, subsection headings
- Color: #1F2937

Body (16px):
- Font Size: 16px
- Font Weight: Regular (400)
- Line Height: 1.5 (24px)
- Usage: Primary body text, descriptions
- Color: #374151

Body Small (14px):
- Font Size: 14px
- Font Weight: Regular (400)
- Line Height: 1.5 (21px)
- Usage: Secondary text, input labels
- Color: #6B7280

Caption (12px):
- Font Size: 12px
- Font Weight: Regular (400)
- Line Height: 1.4 (17px)
- Usage: Timestamps, captions, metadata
- Color: #9CA3AF

Micro (10px):
- Font Size: 10px
- Font Weight: Regular (400)
- Line Height: 1.4 (14px)
- Usage: Status badges, small labels
- Color: #6B7280

FONT SCALE:
10 → 12 → 14 → 16 → 20 → 24 → 32
(Use only these sizes for consistency)

================================================================================
2. COLOR SYSTEM
================================================================================

PRIMARY PALETTE:

Primary Blue:
- Value: #0066CC
- RGB: 0, 102, 204
- Usage: Main UI elements, navigation, CTAs
- Hover: #0052A3
- Active: #003D7A
- Disabled: #E6EFFE

Success Green:
- Value: #10B981
- RGB: 16, 185, 129
- Usage: Stock-in, positive actions, confirmations
- Hover: #059669
- Active: #047857
- Disabled: #D1FAE5

Warning Orange:
- Value: #F59E0B
- RGB: 245, 158, 11
- Usage: Low stock alerts, caution states
- Hover: #D97706
- Active: #B45309
- Disabled: #FEF3C7

Critical Red:
- Value: #EF4444
- RGB: 239, 68, 68
- Usage: Out of stock, errors, delete actions
- Hover: #DC2626
- Active: #B91C1C
- Disabled: #FEE2E2

NEUTRAL PALETTE:

Dark Text:
- Value: #1F2937
- RGB: 31, 41, 55
- Usage: Primary text
- 90% opacity: #1F2937 E6
- 60% opacity: #1F2937 99
- 40% opacity: #1F2937 66

Medium Text:
- Value: #6B7280
- RGB: 107, 114, 128
- Usage: Secondary text, labels
- 70% opacity: #6B7280 B3

Light Gray:
- Value: #9CA3AF
- RGB: 156, 163, 175
- Usage: Disabled text, hints
- 50% opacity: #9CA3AF 80

Very Light Gray:
- Value: #E5E7EB
- RGB: 229, 231, 235
- Usage: Borders, dividers
- 50% opacity: #E5E7EB 80

Background:
- Value: #F9FAFB
- RGB: 249, 250, 251
- Usage: Screen background
- Alternative (cards): #FFFFFF

SEMANTIC COLORS:

Information (Info):
- Color: #0066CC (Primary Blue)
- Background: #EFF6FF (light blue)
- Border: #0066CC

Success:
- Color: #10B981 (Success Green)
- Background: #ECFDF5 (light green)
- Border: #10B981

Warning:
- Color: #F59E0B (Warning Orange)
- Background: #FFFBEB (light orange)
- Border: #F59E0B

Error:
- Color: #EF4444 (Critical Red)
- Background: #FEE2E2 (light red)
- Border: #EF4444

DARK MODE (Future):
- Background: #1F2937
- Surface: #374151
- Text: #F9FAFB
- Text Secondary: #D1D5DB
- Border: #4B5563

================================================================================
3. SPACING SYSTEM
================================================================================

Base Unit: 4px

Scale:
- 2px (0.5x)
- 4px (1x)
- 8px (2x)
- 12px (3x)
- 16px (4x) ← STANDARD PADDING
- 20px (5x)
- 24px (6x)
- 32px (8x)
- 40px (10x)
- 48px (12x)
- 56px (14x)
- 64px (16x)

USAGE PATTERNS:

Screen Padding:
- Top/Bottom: 16px
- Left/Right: 16px
- Safe area respected on notched devices

Card Padding:
- Interior padding: 12px (for compact) or 16px (for spacious)
- External margin: 16px from edges

List Item Padding:
- Horizontal: 16px
- Vertical: 12px
- Divider: Full width minus 16px margins

Button Padding:
- Horizontal: 16px
- Vertical: 12px (internal to hit 48px height)

Input Field Padding:
- Horizontal: 12px
- Vertical: 12px (internal to hit 48px height)

Margin Between Sections:
- Standard: 24px
- Compact: 16px

Gap Between Components:
- Components in row: 8px
- Components in column: 12px

================================================================================
4. COMPONENT SPECIFICATIONS
================================================================================

BUTTONS

Primary Button:
- Background: #0066CC (Primary Blue)
- Text: White, 16px, Semi-bold
- Padding: 12px horizontal, 12px vertical
- Height: 48px (including padding)
- Border radius: 8px
- Shadow: 0px 2px 4px rgba(0, 0, 0, 0.1)
- States:
  * Default: As above
  * Hover: Background #0052A3 (darker blue)
  * Pressed: Scale 1.02x, shadow 0px 4px 8px
  * Disabled: Background #E6EFFE, text #B3D9FF, opacity 50%
  * Loading: Show spinner inside button

Secondary Button:
- Background: Transparent
- Border: 2px solid #0066CC (Primary Blue)
- Text: #0066CC, 16px, Semi-bold
- Padding: 10px horizontal (minus border), 12px vertical
- Height: 48px
- Border radius: 8px
- States: Similar to primary
- Usage: "Cancel", "Skip", secondary actions

Success Button:
- Background: #10B981 (Success Green)
- Text: White, 16px, Semi-bold
- Padding: 12px, Height: 48px
- States: Same as primary button, hover #059669
- Usage: "Stock In", "Confirm", positive actions

Warning Button:
- Background: #F59E0B (Warning Orange)
- Text: White, 16px, Semi-bold
- Padding: 12px, Height: 48px
- States: Same as primary, hover #D97706
- Usage: "Stock Out", caution actions

Danger Button:
- Background: #EF4444 (Critical Red)
- Text: White, 16px, Semi-bold
- Padding: 12px, Height: 48px
- States: Same as primary, hover #DC2626
- Usage: "Delete", "Logout", destructive actions

Small Button:
- Height: 40px (instead of 48px)
- Text: 14px (instead of 16px)
- Padding: 8px horizontal, 8px vertical
- Usage: Secondary actions, quick buttons

Icon Button:
- Size: 48x48px
- Icon: 24x24px, centered
- Background: Transparent (or light on hover)
- No text label
- Usage: Action buttons, navigation

Floating Action Button (FAB):
- Shape: Circle
- Diameter: 56px
- Icon: 24x24px, centered, white
- Background: Primary Blue (#0066CC) or Success Green (#10B981)
- Shadow: 0px 4px 12px rgba(0, 0, 0, 0.15)
- Position: Bottom-right, 16px margin from edges
- Hover: Slightly larger shadow
- Pressed: Scale 1.05x

INPUT FIELDS

Text Input:
- Height: 48px
- Padding: 12px horizontal, 12px vertical
- Border: 2px solid #E5E7EB
- Border radius: 8px
- Font: Body (16px), #1F2937
- Placeholder: 14px, #9CA3AF
- Icon (optional): 24x24px, left or right side, 12px margin from edge
- States:
  * Default: Border #E5E7EB, background white
  * Focus: Border #0066CC, background white, shadow 0px 0px 0px 3px #EFF6FF
  * Filled: Placeholder hidden, value shown
  * Disabled: Background #F3F4F6, text #D1D5DB, border #D1D5DB
  * Error: Border #EF4444, background #FEE2E2, error text below in red

Password Input:
- Same as text input
- Show/hide toggle: Icon on right side
- Icon changes on tap: eye (show) / eye-slash (hide)

Select/Dropdown:
- Same height/border/padding as text input
- Icon: Chevron-down (24x24px) on right side
- On tap: Open modal or popover with options
- Current value shown in field
- Multiple selection indicator: Checkmarks in list

Textarea:
- Min height: 80px
- Same border/padding as text input
- Allow multi-line input
- Character counter (optional): "0 / 500 characters"

Toggle Switch:
- Width: 50px, Height: 28px
- Knob: 24x24px circle
- Background (off): #D1D5DB (gray)
- Background (on): #10B981 (green)
- Knob (off): White, left side
- Knob (on): White, right side
- Transition: 200ms
- States:
  * Off: Gray background, white knob left
  * On: Green background, white knob right
  * Disabled: 50% opacity

Radio Button:
- Size: 20x20px circle
- Border: 2px solid #E5E7EB
- Border radius: 50%
- Checked: Inner circle #0066CC, border #0066CC
- States:
  * Unchecked: Border #E5E7EB, transparent inside
  * Checked: Blue circle inside, border blue
  * Disabled: 50% opacity

Checkbox:
- Size: 20x20px square
- Border: 2px solid #E5E7EB
- Border radius: 4px
- Checked: Blue background (#0066CC), white checkmark
- States:
  * Unchecked: Border #E5E7EB, transparent inside
  * Checked: Blue background, white checkmark
  * Disabled: 50% opacity

CARDS

Standard Card:
- Background: White
- Border: None (use shadow for elevation)
- Border radius: 8px
- Padding: 12px (compact) or 16px (spacious)
- Shadow: 0px 1px 3px rgba(0, 0, 0, 0.1)
- Margin: 8px between cards (vertical)
- On hover: Shadow 0px 2px 6px rgba(0, 0, 0, 0.15)

Metric Card:
- Background: White or light colored (#F3F4F6)
- Padding: 12px
- Height: ~120px
- Content:
  * Large number: 24px, bold
  * Label: 12px, gray
  * Icon: 20px, colored
  * Trend (optional): 12px, green/red

Alert Card:
- Background: Colored light background (light blue, light orange, light red)
- Border-left: 4px solid (colored)
- Padding: 12px
- Icon + text layout
- Colors:
  * Info: Light blue background, blue border, blue icon
  * Warning: Light orange background, orange border, orange icon
  * Error: Light red background, red border, red icon

BADGES & LABELS

Badge (Pill-shaped):
- Padding: 4px horizontal, 4px vertical
- Border radius: 12px (pill shape)
- Font: 10px, bold
- Colors: Colored background, white text
- Usage: Status, counts, labels
- Examples:
  * Success: Green background, white text
  * Warning: Orange background, white text
  * Error: Red background, white text
  * Info: Blue background, white text

Status Badge:
- Small pill-shaped badge
- Text: 10px, bold
- Options:
  * "Healthy" (green)
  * "Low Stock" (orange)
  * "Out of Stock" (red)

Count Badge:
- Small circle badge (20x20px)
- Number centered, white text
- Background: Orange or red
- Positioned: Top-right of icon/button
- Usage: Notification count, item count

DIVIDERS & SEPARATORS

Divider Line:
- Color: #E5E7EB
- Height: 1px
- Width: Full width minus margins (16px on each side)
- Margin: 12px top/bottom

Card Divider:
- Color: #E5E7EB
- Height: 1px
- Margin: 12px top/bottom within card

Section Divider:
- Color: #E5E7EB
- Height: 1px
- Full width
- Margin: 24px top/bottom

BOTTOM NAVIGATION

Height: 56px
Background: White
Border: 1px solid #E5E7EB (top)
5 Tab items:
- Icon: 24x24px
- Label: 12px, below icon
- Color (inactive): #6B7280
- Color (active): #0066CC
- Badge: Optional count badge, top-right of icon
- Active tab: Blue icon + label, background light blue
- Tap area: Full tab width/height (48px each)
- Labels always shown (not hidden on mobile like iOS standard)

MODALS & DIALOGS

Standard Modal:
- Overlay: Semi-transparent black, 60% opacity
- Content: White card, rounded corners (8px)
- Padding: 16px
- Width: Full width minus 32px margins
- Height: Fit content (max 80% screen height)
- Shadow: 0px 4px 16px rgba(0, 0, 0, 0.2)
- Animation: Fade in from center + scale (1.0 → 1.1)

Confirmation Modal:
- Title: 20px, bold
- Content: 14px, gray
- Buttons: 2 buttons below (Cancel, Confirm)
- Button layout: Side-by-side (if space) or stacked
- Colors: Cancel (gray), Confirm (blue/green/red based on action)

Bottom Sheet Modal:
- Slides up from bottom
- Background: White
- Border radius: 12px (top corners only)
- Padding: 16px
- Drag handle: Small gray bar at top (optional)
- Content: Scrollable if needed
- Animation: Slide up + fade

================================================================================
5. ICONS SPECIFICATIONS
================================================================================

Size Standards:
- 16px: Small labels, inline icons
- 20px: Badges, list items
- 24px: Standard UI icons, buttons
- 32px: Large actions, emphasis
- 48px: Large actions, prominent

Style:
- Outline style (stroke-based)
- Stroke width: 1.5px - 2px
- Consistent weight across all icons
- Rounded line caps and joins
- Colors: Match context (blue, green, orange, red, gray)

Icon Library Sources:
- Use consistent icon set (e.g., Feather Icons, Material Icons)
- Create custom icons for THROVE-specific elements
- All icons in SVG format for scalability

Common Icons Needed:
- Navigation: home, package, chart-bar, settings, menu, chevron-left, chevron-right, chevron-down
- Actions: plus, edit, delete, copy, download, share, refresh, search, filter
- Status: check, check-circle, alert-circle, alert, x, x-circle, info
- Inventory: box, package, inbox, shopping-cart, trending-up, trending-down
- Time: clock, calendar, timer
- Business: briefcase, building, map-pin, phone, mail
- Settings: bell, lock, eye, eye-off, sun, moon, globe
- File: file, file-pdf, download

Color Usage:
- Primary actions: Primary blue (#0066CC)
- Success: Success green (#10B981)
- Warning: Warning orange (#F59E0B)
- Error: Critical red (#EF4444)
- Neutral: Medium gray (#6B7280)
- Disabled: Light gray (#D1D5DB)

================================================================================
6. CHART & DATA VISUALIZATION
================================================================================

CHARTS:

Line Chart:
- Line color: Primary blue (#0066CC)
- Line width: 2px
- Dots: 4px diameter, blue
- Grid: Light gray (#E5E7EB), 1px
- Background: Transparent or light (#F9FAFB)
- Axis labels: 12px, gray
- Axis lines: 1px, #E5E7EB
- Interactive: Tap point to show tooltip
- Tooltip: White background, shadow, 12px text, positioned above point

Bar Chart:
- Bar color (default): Primary blue (#0066CC)
- Bar color (warning): Warning orange (#F59E0B)
- Bar color (alert): Critical red (#EF4444)
- Bar width: Proportional to space
- Gap between bars: 25% of bar width
- Grid: Light gray (#E5E7EB), 1px
- Axis labels: 12px, gray
- Value labels: On top of bar or inside if space

Pie Chart:
- Segments: Colorful palette (blue, green, orange, red, purple, teal)
- Segment spacing: 2px gap
- Center label (optional): Total or main metric
- Legend: Below chart, grid layout
- Interactive: Tap segment to highlight and show percentage

Area Chart:
- Area fill: Primary blue (#0066CC), 20% opacity
- Line: Primary blue (#0066CC), 2px
- Grid: Light gray (#E5E7EB)
- Similar interaction to line chart

LEGENDS:

Position: Below chart (default) or right side (for space)
Layout: Grid (2-3 columns) or single row
Item spacing: 12px between items
Format: Color square (12x12px) + label (12px text)
Interactive: Tap to toggle series visibility

TOOLTIPS:

Style:
- Background: Dark gray (#374151), rounded (4px)
- Text: White, 12px
- Padding: 8px
- Arrow: Pointing to data point
- Shadow: 0px 2px 8px rgba(0, 0, 0, 0.2)
- Max width: 120px
- Position: Above point by default, flip if near top

Content:
- Date/label on first line (bold)
- Value on second line
- Currency symbol included (₦)
- Unit included (units, %, etc.)

LOADING STATES:

Spinner:
- Style: Rotating circle
- Color: Primary blue (#0066CC)
- Size: 32px (medium), 48px (large)
- Stroke width: 4px
- Duration: 1.5 seconds
- Animation: Smooth rotation

Skeleton Screen:
- Placeholder blocks matching content
- Color: Light gray (#E5E7EB)
- Animation: Shimmer effect (left to right, 1.5s duration)
- Use for: Card lists, product lists, analytics

Progress Bar:
- Background: Light gray (#E5E7EB)
- Filled: Primary blue (#0066CC)
- Height: 4px (small) or 8px (medium)
- Border radius: 2px
- Label: Percentage text above bar
- Animation: Smooth fill transition

================================================================================
7. ANIMATIONS & TRANSITIONS
================================================================================

SCREEN TRANSITIONS:

Default transition:
- Duration: 300ms
- Easing: ease-in-out (cubic-bezier(0.4, 0, 0.2, 1))
- Direction: Left to right for back, right to left for forward

Fade transition:
- Fade out: 150ms
- Fade in: 150ms
- Total: 300ms

Slide transition:
- Slide out: 300ms (current screen slides left)
- Slide in: 300ms (new screen slides in from right)
- Distance: 100% screen width

INTERACTION ANIMATIONS:

Button tap:
- Animation: Scale 1.02x
- Duration: 100ms
- Easing: ease-out
- On release: Return to 1.0x
- + Haptic feedback (light pulse)

Card interaction:
- Hover: Subtle shadow increase
- Press: Scale 0.98x, shadow decrease
- Duration: 100ms

Swipe action:
- Reveal actions: 200ms slide
- Action taken: 300ms slide out + fade

Toggle switch:
- Animation: Knob slides, background changes
- Duration: 200ms
- Easing: ease-in-out

Micro-interaction (success):
- Checkmark appears: Scale 0 → 1.0x (200ms)
- Bounce: Scale 1.0 → 1.1 → 1.0 (100ms)
- Total: 300ms

Error shake:
- Shake left-right: 50px swing
- Duration: 300ms total (4 shakes)
- Easing: ease-in-out

Pull-to-refresh:
- Pull: Icon rotates, text updates
- Release: Spinner appears, content refreshes
- Completion: Spinner disappears, 500ms fade out
- Bounce back: Content slides back up (200ms)

Modal open:
- Overlay fade in: 200ms
- Content scale: 0.8 → 1.0 (300ms)
- Easing: ease-out

Modal close:
- Content scale: 1.0 → 0.8 (200ms)
- Overlay fade out: 200ms
- Easing: ease-in

List item remove:
- Slide left: 300ms
- Fade: 300ms
- Height collapse: 200ms

================================================================================
8. RESPONSIVE DESIGN
================================================================================

BREAKPOINTS:

Small (375px): iPhone SE, older phones
- Single column layouts
- Full-width buttons
- Stacked card layouts

Medium (414px): Standard phones
- Primary breakpoint
- Most designs optimized here
- Occasionally 2-column for lists

Large (768px): Tablets
- 2-column layouts possible
- Wider cards
- Expanded spacing

X-Large (1024px): Large tablets
- 3-column layouts
- Desktop-like layouts (if supporting)

RESPONSIVE RULES:

Column layouts:
- 375-414px: Single column (100% width)
- 600px+: Two columns (50% width, gap 8px)
- 800px+: Three columns (33% width, gap 8px)

Spacing adjustments:
- 375px: Standard 16px (keep consistent)
- 600px+: Can use 20px or 24px padding
- 1024px+: Can use 32px padding

Font size adjustments:
- 375px: Standard sizes (10-32px)
- 600px+: Can increase by 2px if needed
- Never less than 12px for body text

Button width:
- 375px: Full width (minus 16px margins)
- 600px+: Can be constrained to 400px max width, centered

Bottom navigation:
- 375px: 5 tabs with labels (required)
- 600px+: Can hide labels if space needed
- 1024px+: Move to side navigation (optional)

================================================================================
9. DARK MODE (FUTURE IMPLEMENTATION)
================================================================================

Color mappings:

Light Mode → Dark Mode

White (#FFFFFF) → Dark surface (#1F2937)
#F9FAFB → #111827
#E5E7EB → #4B5563
#1F2937 → #F9FAFB
#6B7280 → #D1D5DB
#0066CC → #60A5FA (lighter blue for dark backgrounds)
#10B981 → #34D399 (lighter green)
#F59E0B → #FBBF24 (lighter orange)
#EF4444 → #F87171 (lighter red)

Dark mode rules:
- Toggle in Settings
- Apply to all screens
- Maintain contrast (4.5:1 for text)
- Use lighter shades for semantic colors
- Preserve hierarchy and readability

================================================================================
END OF DESIGN SYSTEM
================================================================================
