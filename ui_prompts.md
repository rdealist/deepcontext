# DeepContext UI Development Prompts

Use these prompts to assist AI agents (or yourself) in generating code that adheres to the DeepContext UI Design Specification.

## General UI Task Prompt
```text
I need to implement a new feature/page for the DeepContext application.
Please adhere strictly to the project's UI Design Specification:
- **Font**: Use 'Space Grotesk' for headings and 'Noto Sans' for body.
- **Colors**: Use the `bg-background` (Stone-50) and `bg-card` (White) pattern. Primary action color is Green-500.
- **Styling**: Use 'rounded-xl' for cards, 'rounded-lg' for inputs/buttons. Add subtle shadows (`shadow-sm`, `shadow-md`).
- **Tailwind**: Use the semantic variables defined in `globals.css` (e.g., `bg-primary`, `text-muted-foreground`).

Current Task: [Describe your task here]
```

## Component Generation Prompt
```text
Create a [Component Name] component using React and Tailwind CSS.
Style Requirements:
- Wrapper: `bg-white border border-stone-200 shadow-sm rounded-xl`
- Heading: `font-heading font-bold text-stone-800`
- Body Text: `font-sans text-stone-600`
- Interactive Elements: Hover effects should use `hover:shadow-md` or `hover:bg-stone-50`.
- Primary Button: `bg-green-500 hover:bg-green-600 text-white`
```

## Page Layout Prompt
```text
Create a layout for the [Page Name] page.
- Root: `min-h-screen bg-stone-50 text-stone-900`
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8`
- Header: Minimalist, `border-b border-stone-200 bg-white/80 backdrop-blur-md`
- Content: Grid or Flex layout with `gap-6` or `gap-8`.
```

## Refactoring Prompt
```text
Refactor the following code to match the "Plant Care" design aesthetic:
- Change gray backgrounds to warmer `stone` colors (e.g., `bg-gray-100` -> `bg-stone-50`).
- Change primary blue/indigo colors to `green-500` (#22c55e).
- Update border radius to be slightly larger (`rounded-lg` -> `rounded-xl` for cards).
- Ensure typography uses `font-heading` for titles and `font-sans` for text.
```
