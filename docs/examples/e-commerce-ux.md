# Example: E-commerce Checkout UX Evaluation

This example shows how to use DesignOS to evaluate an e-commerce checkout flow and identify usability issues.

## Scenario

**Company:** Online fashion retailer  
**Problem:** High cart abandonment rate (68%)  
**Goal:** Identify and fix UX issues in the checkout flow

## Files Provided

```
project/
├── screenshots/
│   ├── 01-cart-summary.png
│   ├── 02-shipping-address.png
│   ├── 03-payment-method.png
│   └── 04-order-confirmation.png
├── docs/
│   └── checkout-prd.md
└── analytics/
    └── user-session-recordings.mp4
```

## Step 1: Run UX Evaluation

```bash
/uxeval screenshots/ --prd docs/checkout-prd.md
```

## Step 2: Review Generated Output

### Journey Map (`output/uxeval/journey-map.md`)

```markdown
## User Journey: Checkout Flow

### Stage 1: Cart Review
**Goal:** Verify order details before proceeding

**User actions:**
- Review item list
- Update quantities
- Apply promo code
- Click "Proceed to Checkout"

**Pain points:**
- ❌ Promo code field hidden in collapsed section
- ❌ No clear indication of shipping cost
...
```

### Issues Report (`output/uxeval/issues.md`)

```markdown
## Critical Issues (Severity: High)

### 1. Hidden Shipping Cost (Nielsen Principle: Visibility of System Status)
**Location:** Cart Summary page
**Description:** Shipping cost not shown until payment page, causing surprise and abandonment.
**Recommendation:** Show estimated shipping on cart page.
**Impact:** ~15% reduction in abandonment expected

### 2. Required Field Not Marked
**Location:** Shipping Address form
**Description:** "Apartment #" field appears required but isn't marked.
...
```

## Step 3: Prioritize Fixes

DesignOS automatically prioritizes issues by:
- **Severity** (High / Medium / Low)
- **Frequency** (How many users affected)
- **Fix complexity** (Easy / Medium / Hard)

**Top 3 Quick Wins:**
1. Show shipping estimate on cart page (1-day fix, -15% abandonment)
2. Mark optional fields clearly (2-hour fix, -8% form errors)
3. Add promo code visibility (1-day fix, +12% code usage)

## Step 4: Implement & Measure

After fixing the top 3 issues:
- **Cart abandonment:** 68% → 52% (-16%)
- **Checkout completion time:** 4.2min → 3.1min (-26%)
- **Support tickets:** -35% (fewer payment confusion cases)

## Key Takeaways

✅ **Automated detection** caught 12 issues human reviewers missed  
✅ **Prioritization** helped focus on high-impact fixes first  
✅ **Evidence-based** recommendations backed by heuristics  
✅ **Fast iteration** — full evaluation in 5 minutes vs 2 hours manual

## Try It Yourself

Download this example:
```bash
git clone <YOUR_INTERNAL_PRIVATE_REPO>-examples.git
cd designos-examples/e-commerce-checkout
npx <YOUR_INTERNAL_PACKAGE>
```

Then run:
```bash
/uxeval screenshots/ --prd docs/checkout-prd.md
```

## Related Examples

- [SaaS Onboarding Flow](saas-onboarding.md)
- [Mobile App Navigation](mobile-navigation.md)
- [Admin Dashboard Redesign](admin-dashboard.md)
