# AI Finance Assistant - UX & Frontend Guide

> Complete guide to user experience design, component library, accessibility, and frontend development for EU developers.

---

## Table of Contents
1. [Design System & Visual Language](#design-system--visual-language)
2. [Component Library](#component-library)
3. [Pages & User Flows](#pages--user-flows)
4. [Conversation Design](#conversation-design)
5. [Visualization Best Practices](#visualization-best-practices)
6. [Accessibility (WCAG 2.1)](#accessibility-wcag-21)
7. [Performance Optimization](#performance-optimization)
8. [Responsive Design](#responsive-design)

---

## Design System & Visual Language

### Color Palette

**Primary Colors:**
```
Blue:        #3B82F6 (Stocks, Primary Action)
Green:       #10B981 (Growth, Positive)
Amber:       #F59E0B (Warning, Caution)
Red:         #EF4444 (Danger, Losses)
Gray:        #6B7280 (Secondary, Text)
```

**Usage Examples:**
```tsx
// Chart colors
const CHART_COLORS = {
  stocks: '#3B82F6',      // Bullish, growth
  bonds: '#10B981',       // Safe, stable
  realEstate: '#F59E0B',  // Medium risk
  crypto: '#8B5CF6',      // High risk
  cash: '#EF4444'         // Preservation
};

// Risk indicators
const RISK_COLORS = {
  low: '#10B981',        // Green - Safe
  moderate: '#F59E0B',   // Amber - Caution
  high: '#EF4444'        // Red - Danger
};
```

### Typography

```css
/* Headings */
h1 { font-size: 32px; font-weight: 700; line-height: 1.2; }
h2 { font-size: 24px; font-weight: 600; line-height: 1.3; }
h3 { font-size: 18px; font-weight: 600; line-height: 1.4; }

/* Body Text */
p  { font-size: 16px; font-weight: 400; line-height: 1.6; }
small { font-size: 12px; font-weight: 400; line-height: 1.5; }

/* Monospace (for code/numbers) */
code { font-family: 'Monaco', 'Courier New'; font-size: 13px; }

/* Font: Inter/System (Tailwind default) */
body { font-family: system-ui, -apple-system, sans-serif; }
```

### Spacing & Sizing

```
Base unit: 4px

Spacing Scale:
xs:  4px   (mb-1)
sm:  8px   (mb-2)
md: 16px   (mb-4)
lg: 24px   (mb-6)
xl: 32px   (mb-8)

Width constraints:
Small:   320px (mobile)
Medium:  768px (tablet)
Large:  1024px (desktop)
XL:     1280px (wide)

Border radius:
Small:  2px   (rounded-sm)
Medium: 4px   (rounded)
Large:  8px   (rounded-lg)
```

### Shadows & Elevation

```css
/* Shadow hierarchy (Tailwind) */
shadow-sm:  0 1px 2px rgba(0,0,0,0.05)
shadow-md:  0 4px 6px rgba(0,0,0,0.1)
shadow-lg:  0 10px 15px rgba(0,0,0,0.1)
shadow-xl:  0 20px 25px rgba(0,0,0,0.1)

/* Usage */
<div className="shadow-md">Card with elevation</div>
```

---

## Component Library

### Chart Components

#### 1. AssetAllocationChart (Pie Chart)

```tsx
interface AssetAllocation {
  name: string;           // "Stocks", "Bonds", etc.
  value: number;          // Dollar amount
  percentage: string;     // "60%"
}

<AssetAllocationChart
  data={[
    { name: 'Stocks', value: 75000, percentage: '60%' },
    { name: 'Bonds', value: 37500, percentage: '30%' },
    { name: 'Cash', value: 12500, percentage: '10%' }
  ]}
  title="Asset Allocation"
/>
```

**Features:**
- Interactive pie chart with labels
- Custom tooltips showing value and percentage
- Summary stats (total value, asset classes, largest position)
- Responsive sizing

**Design Decisions:**
- Pie charts for part-to-whole relationships
- Each color represents asset class
- Tooltips on hover for exact numbers
- Summary cards for key metrics

---

#### 2. RiskHeatmap (Bar Chart + Risk Scoring)

```tsx
interface RiskMetric {
  category: string;         // "Tech Stocks", "International"
  volatility: number;        // 0.25 = 25%
  expectedReturn: number;    // 0.08 = 8%
  riskScore: number;         // 0-100
}

<RiskHeatmap
  data={[
    { category: 'Tech Stocks', volatility: 0.35, expectedReturn: 0.12, riskScore: 75 },
    { category: 'Bonds', volatility: 0.05, expectedReturn: 0.04, riskScore: 20 }
  ]}
  title="Portfolio Risk Analysis"
/>
```

**Features:**
- Dual-axis bar chart (Risk Score vs Expected Return)
- Color-coded risk levels (Green→Red)
- Summary risk level badge
- Detailed position table
- Risk score breakdown

**Design Decisions:**
- Bars show risk score (primary metric)
- Color gradient shows risk intensity
- Tooltip shows all metrics
- Summary badge summarizes overall portfolio risk

---

#### 3. CorrelationMatrix (Heatmap)

```tsx
interface CorrelationData {
  assets: string[];         // ["Stocks", "Bonds", "Crypto"]
  matrix: number[][];       // -1 to 1 correlation coefficients
}

<CorrelationMatrix
  data={{
    assets: ['Stocks', 'Bonds', 'Real Estate'],
    matrix: [
      [1.0, -0.3, 0.2],
      [-0.3, 1.0, 0.5],
      [0.2, 0.5, 1.0]
    ]
  }}
  title="Asset Correlation Matrix"
/>
```

**Features:**
- Matrix grid with color-coded cells
- Cell colors show correlation strength
- Diversification quality score
- Insights panel with recommendations
- Hover tooltips with exact correlation values

**Design Decisions:**
- Grid layout for matrix representation
- Color intensity shows correlation strength
- Negative (inverse) correlations = good (green)
- Positive correlations = bad (red)
- Insights help users understand implications

---

### Chat Components

#### ChatInterface

```tsx
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];      // Knowledge base files
  confidence?: number;      // 0-1
}

<ChatInterface
  conversationId="conv-123"
  messages={[
    { role: 'user', content: 'What is diversification?' },
    { role: 'assistant', content: 'Diversification is...', sources: ['03_diversification.md'] }
  ]}
  onSendMessage={handleMessage}
  loading={isLoading}
/>
```

**Features:**
- Multi-turn conversation support
- Message history with timestamps
- Source attribution for assistant responses
- Confidence badges
- Loading states
- Input auto-focus on load

**Design Principles:**
```
User Messages:
- Aligned right
- Blue background (#3B82F6)
- White text
- Rounded top-left, sharp bottom-right

Assistant Messages:
- Aligned left
- Gray background (#F3F4F6)
- Black text
- Rounded top-right, sharp bottom-left

Layout:
- Scrollable message area
- Fixed input at bottom
- Auto-scroll to latest message
- Loading skeleton while waiting
```

---

#### ConversationHistory

```tsx
interface Conversation {
  id: string;
  createdAt: Date;
  intent: string;        // "tax_planning"
  topics: string[];      // ["tax", "retirement"]
  messageCount: number;
}

<ConversationHistory
  conversations={conversations}
  onSelectConversation={handleSelect}
/>
```

**Design:**
- Sidebar list of previous conversations
- Shows topic tags and message count
- Click to resume conversation
- Delete button on hover
- Search/filter conversations

---

### Layout Components

#### Dashboard Layout

```tsx
<DashboardLayout>
  <Sidebar>
    {/* Navigation + Conversation History */}
  </Sidebar>
  
  <MainContent>
    <Header>
      {/* Title + Settings */}
    </Header>
    
    <TabContent>
      {/* Chat / Portfolio / Analysis */}
    </TabContent>
  </MainContent>
</DashboardLayout>
```

**Responsive Breakpoints:**
```
Mobile (< 640px):
- Sidebar collapses
- Full-width content
- Bottom navigation

Tablet (640px - 1024px):
- Sidebar slides out on menu click
- Content takes remaining space

Desktop (> 1024px):
- Sidebar always visible
- 3-column layout possible
```

---

## Pages & User Flows

### Page 1: Chat Interface

```
┌─────────────────────────────────────────┐
│           Chat Interface                 │
├────────────────┬────────────────────────┤
│  Conversations │  Active Conversation   │
│  ─────────────  ├────────────────────────┤
│  • Finance QA  │                        │
│  • Tax Plan    │   [Message History]    │
│  • Portfolio   │   [Scrollable Area]    │
│    Analysis    │                        │
│                │ ┌────────────────────┐ │
│ [+ New Conv]   │ │ [Input Area]       │ │
│                │ │ "Ask me anything"  │ │
│                │ │ [Send Button]      │ │
│                │ └────────────────────┘ │
└────────────────┴────────────────────────┘
```

**User Flow:**
```
1. User opens app
2. Existing conversations show in sidebar
3. User can:
   a. Click conversation to resume
   b. Click "+ New Conversation" to start fresh
4. User types message
5. Message appears in chat (right-aligned)
6. Assistant response appears (left-aligned)
7. Sources shown below response
8. User can continue conversation or start new one

Context Persistence:
- Each message builds on previous conversation
- System remembers user preferences mentioned
- RAG retriever includes conversation context
- Multi-turn queries improve in specificity
```

### Page 2: Portfolio Analysis

```
┌──────────────────────────────────────────┐
│        Portfolio Analysis                │
├──────────────────────────────────────────┤
│                                          │
│  ┌─────────────────┬─────────────────┐  │
│  │ Asset Allocation│    Risk Heat    │  │
│  │    (Pie Chart)  │     Map         │  │
│  │                 │   (Bar Chart)   │  │
│  └─────────────────┴─────────────────┘  │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Correlation Matrix              │   │
│  │  [Asset Classes]                 │   │
│  │  [Color-coded correlations]      │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Portfolio Insights              │   │
│  │  • Diversification Score: Good   │   │
│  │  • Risk Level: Moderate          │   │
│  │  • Recommendations...            │   │
│  └──────────────────────────────────┘   │
│                                          │
└──────────────────────────────────────────┘
```

**Interaction:**
- Hover on charts for details
- Click on data points to drill down
- Resize charts responsively
- Export data as CSV/PDF

---

## Conversation Design

### Multi-turn Conversation UX

**Message Context Persistence:**

```
User: "What's dollar-cost averaging?"
↓
Assistant: "DCA is an investment strategy where..."
[Sources: 07_dca.md]

User: "How much should I invest monthly?"
↓
System thinks: "User is interested in DCA. 
They're now asking for practical advice."
↓
Assistant: "The amount depends on your income and goals. 
Given your interest in DCA, a common approach is..."
[Sources: 07_dca.md, 41_financial_goals.md]

User: "What if the market crashes?"
↓
System thinks: "User learning about DCA, asking about 
market volatility risk. Recall DCA as volatility hedge."
↓
Assistant: "DCA actually helps during crashes! 
You buy more shares when prices are low..."
[Sources: 07_dca.md, 14_market_volatility.md]
```

**Visual Feedback:**

```tsx
// Message shows conversation context
<ChatMessage>
  <MessageBubble role="assistant">
    <Content>
      "DCA actually helps during crashes..."
    </Content>
    
    <Footer>
      <Badge>Continuing on: Dollar-Cost Averaging</Badge>
      <Sources>
        <Source>07_dca.md</Source>
        <Source>14_market_volatility.md</Source>
      </Sources>
      <Confidence score={0.92}>High Confidence</Confidence>
    </Footer>
  </MessageBubble>
</ChatMessage>
```

### Conversation Settings

```tsx
<ConversationSettings>
  <Setting label="Conversation Title">
    <Input value="DCA Investment Strategy" />
  </Setting>
  
  <Setting label="Show Sources">
    <Toggle defaultChecked={true} />
  </Setting>
  
  <Setting label="Detail Level">
    <Radio options={['Brief', 'Standard', 'Detailed']} value="Standard" />
  </Setting>
  
  <Setting label="Clear History">
    <Button onClick={clearHistory}>Clear Messages</Button>
  </Setting>
</ConversationSettings>
```

---

## Visualization Best Practices

### When to Use Each Chart

| Chart Type | Best For | Example |
|-----------|----------|---------|
| **Pie Chart** | Part-to-whole | Asset allocation (60% stocks, 30% bonds) |
| **Bar Chart** | Comparing values | Risk scores across positions |
| **Line Chart** | Trends over time | Portfolio value over 1 year |
| **Heatmap** | Matrix data | Asset correlations |
| **Table** | Precise values | Position details, holdings |

### Data Label Guidelines

```tsx
// Good: Clear, concise labels
<Pie dataKey="value" name="Portfolio Value" />

// Bad: Too many labels, overlapping
<Pie dataKey="value" label={({ name, value, percentage }) => 
  `${name}: $${value.toLocaleString()} (${percentage}%)`} />

// Better: Tooltip with details
<Tooltip content={<CustomTooltip />} />
```

### Color Accessibility

```
Avoid:
- Red + Green only (colorblind users)
- Low contrast (< 4.5:1 ratio)
- Unfamiliar color meanings

Use:
- Pattern + color (hatching for B&W printing)
- Text labels + color
- High contrast (7:1 for AAA)
- Consistent color meanings
```

---

## Accessibility (WCAG 2.1)

### Keyboard Navigation

```tsx
// All interactive elements are keyboard accessible
<button
  onClick={handleClick}
  aria-label="Send message"
  tabIndex={0}
>
  Send
</button>

// Tab order is logical (top-to-bottom, left-to-right)
<form>
  <input placeholder="User input" tabIndex={1} />
  <button tabIndex={2}>Submit</button>
  <button tabIndex={3}>Cancel</button>
</form>
```

### Screen Reader Support

```tsx
// Aria labels for icons/images
<img src="chart.svg" alt="Portfolio allocation pie chart" />

// Aria descriptions for complex components
<div
  role="img"
  aria-label="Asset allocation chart"
  aria-describedby="chart-description"
>
  <Chart data={data} />
</div>
<p id="chart-description">Shows 60% stocks, 30% bonds, 10% cash</p>

// Live region for dynamic updates
<div aria-live="polite" aria-atomic="true">
  Message sent successfully!
</div>
```

### Color Contrast

```
Minimum: 4.5:1 (AA)
Enhanced: 7:1 (AAA)

Examples:
✓ #3B82F6 (Blue) on #FFFFFF (White) = 8.6:1 ✓
✓ #10B981 (Green) on #FFFFFF (White) = 5.1:1 ✓
✗ #F59E0B (Amber) on #FFFFFF (White) = 3.2:1 ✗
```

### Text Sizing

```css
/* Minimum 14px, recommended 16px+ */
body { font-size: 16px; }

/* Support zoom up to 200% without horizontal scrolling */
max-width: 100%;
overflow-x: hidden;

/* Focus indicators visible (min 3:1 contrast) */
button:focus {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}
```

---

## Performance Optimization

### Code Splitting

```tsx
// Lazy load pages
const ChatPage = lazy(() => import('./pages/Chat'));
const PortfolioPage = lazy(() => import('./pages/Portfolio'));

<Suspense fallback={<Skeleton />}>
  <ChatPage />
</Suspense>
```

### Image Optimization

```tsx
// Responsive images with srcset
<img
  src="chart-small.png"
  srcSet="
    chart-small.png 480w,
    chart-medium.png 768w,
    chart-large.png 1200w
  "
  alt="Portfolio chart"
/>

// Lazy load below-the-fold images
<img
  src="..."
  loading="lazy"
  alt="..."
/>
```

### React Performance

```tsx
// Memoize expensive calculations
const diversificationScore = useMemo(() => {
  return calculateDiversification(data);
}, [data]);

// Memoize components
const ChartComponent = memo(({ data }) => (
  <Chart data={data} />
));

// Use useCallback for event handlers
const handleMessage = useCallback((msg) => {
  sendMessage(msg);
}, []);
```

### Bundle Size

```
Current: ~250KB (gzipped)
Target: < 200KB

Optimizations:
- Tree-shaking unused code
- Dynamic imports for large libraries
- Upgrade to latest Recharts
- Remove unused Tailwind classes
```

---

## Responsive Design

### Mobile First Approach

```tsx
// Default (mobile) styles
<div className="w-full px-4 py-2">
  {/* Mobile layout */}
</div>

// Tablet
<div className="md:px-6 md:py-4">
  {/* Tablet layout */}
</div>

// Desktop
<div className="lg:w-3/4 lg:mx-auto">
  {/* Desktop layout */}
</div>
```

### Breakpoints (Tailwind)

| Name | Width |
|------|-------|
| sm   | 640px |
| md   | 768px |
| lg   | 1024px|
| xl   | 1280px|

### Responsive Chart Sizing

```tsx
// Charts resize based on container
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    {/* Dynamic sizing */}
  </BarChart>
</ResponsiveContainer>

// CSS-based sizing fallback
@media (max-width: 640px) {
  .chart { height: 250px; }
}
@media (min-width: 641px) and (max-width: 1024px) {
  .chart { height: 350px; }
}
@media (min-width: 1025px) {
  .chart { height: 400px; }
}
```

---

## Component Development Guide

### Creating New Components

```tsx
// 1. Define types
interface Props {
  data: DataType[];
  title?: string;
  onSelect?: (item: DataType) => void;
}

// 2. Create component
export const MyComponent: React.FC<Props> = ({
  data,
  title = 'Default Title',
  onSelect
}) => {
  // 3. Add hooks
  const [selected, setSelected] = useState<string | null>(null);
  
  // 4. Add effects
  useEffect(() => {
    // Initialize data
  }, [data]);
  
  // 5. Render with Tailwind classes
  return (
    <div className="w-full bg-white rounded-lg shadow-md p-6">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      {/* Component content */}
    </div>
  );
};

// 6. Export
export default MyComponent;
```

### Testing Components

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('MyComponent', () => {
  it('renders with title', () => {
    render(<MyComponent data={[]} title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
  
  it('calls onSelect when item clicked', async () => {
    const handleSelect = jest.fn();
    const { user } = render(
      <MyComponent data={[{ id: '1', name: 'Item' }]} onSelect={handleSelect} />
    );
    await user.click(screen.getByText('Item'));
    expect(handleSelect).toHaveBeenCalled();
  });
});
```

---

## Design Tokens (Reference)

```json
{
  "colors": {
    "primary": "#3B82F6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444"
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "typography": {
    "fontSize": {
      "xs": "12px",
      "sm": "14px",
      "base": "16px",
      "lg": "18px",
      "xl": "20px"
    },
    "fontWeight": {
      "normal": 400,
      "semibold": 600,
      "bold": 700
    }
  },
  "borderRadius": {
    "sm": "2px",
    "md": "4px",
    "lg": "8px"
  },
  "shadows": {
    "sm": "0 1px 2px rgba(0,0,0,0.05)",
    "md": "0 4px 6px rgba(0,0,0,0.1)",
    "lg": "0 10px 15px rgba(0,0,0,0.1)"
  }
}
```

---

## Common UX Patterns

### Loading States

```tsx
// Skeleton loader
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded mb-2"></div>
  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
</div>

// Loading spinner
<div className="animate-spin">
  <svg>...</svg>
</div>

// Progress bar
<div className="bg-gray-200 h-2 rounded">
  <div className="bg-blue-500 h-full rounded" style={{ width: '65%' }}></div>
</div>
```

### Error Handling

```tsx
// Error banner
<div className="bg-red-50 border border-red-200 rounded p-4 text-red-800">
  <strong>Error:</strong> Failed to load data. Please try again.
  <button className="underline">Retry</button>
</div>

// Toast notification
<toast>
  <span className="text-green-700">✓ Changes saved</span>
</toast>
```

### Empty States

```tsx
// Empty state
<div className="text-center py-12">
  <svg className="mx-auto h-12 w-12 text-gray-400">...</svg>
  <h3 className="mt-2 text-sm font-semibold text-gray-900">No data</h3>
  <p className="mt-1 text-sm text-gray-500">Get started by loading your portfolio.</p>
  <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">Load Data</button>
</div>
```

---

**Last Updated**: April 2026 | **For**: EU Frontend Developers
