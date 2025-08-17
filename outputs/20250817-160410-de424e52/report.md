# Data Analyst Agent — Report

## Profile
- Rows: **10**
- Columns: **6**
- Duplicates: **0**
- Memory: **0.002 MB**

### Dtypes

- `order_id`: int64
- `customer`: object
- `category`: object
- `quantity`: int64
- `price`: float64
- `date`: object

### Missing by Column

- `order_id`: 0
- `customer`: 0
- `category`: 0
- `quantity`: 0
- `price`: 0
- `date`: 0

## Summary Statistics

```json
{
  "order_id": {
    "count": 10.0,
    "mean": 5.5,
    "std": 3.0276503540974917,
    "min": 1.0,
    "25%": 3.25,
    "50%": 5.5,
    "75%": 7.75,
    "max": 10.0
  },
  "quantity": {
    "count": 10.0,
    "mean": 3.6,
    "std": 2.988868236194653,
    "min": 1.0,
    "25%": 1.25,
    "50%": 2.5,
    "75%": 4.75,
    "max": 10.0
  },
  "price": {
    "count": 10.0,
    "mean": 71.28,
    "std": 106.12949951199558,
    "min": 2.3,
    "25%": 4.9,
    "50%": 11.75,
    "75%": 117.75,
    "max": 299.0
  }
}
```

## Correlations/Associations

![Pearson Heatmap](/outputs/20250817-160410-de424e52/corr_heatmap.png)
### Spearman top pairs
- quantity ↔ price: -0.775
- order_id ↔ quantity: 0.129
- order_id ↔ price: 0.067
### Categorical association (heuristic)
- customer ↔ category: score=0.200
- customer ↔ date: score=0.100
- category ↔ date: score=0.100

## Visuals

![hist_order_id.png](/outputs/20250817-160410-de424e52/hist_order_id.png)
![box_order_id.png](/outputs/20250817-160410-de424e52/box_order_id.png)
![hist_quantity.png](/outputs/20250817-160410-de424e52/hist_quantity.png)
![box_quantity.png](/outputs/20250817-160410-de424e52/box_quantity.png)
![hist_price.png](/outputs/20250817-160410-de424e52/hist_price.png)
![box_price.png](/outputs/20250817-160410-de424e52/box_price.png)
![bar_customer.png](/outputs/20250817-160410-de424e52/bar_customer.png)
![bar_category.png](/outputs/20250817-160410-de424e52/bar_category.png)
![bar_date.png](/outputs/20250817-160410-de424e52/bar_date.png)

## Answers

**Q:** How many rows are there?

**A:** Rows: 10

**Q:** How many columns are there?

**A:** Columns: 6

**Q:** What is the correlation between quantity and price?

**A:** Question recorded, but no automatic answer.

**Q:** Which category has the highest number of orders?

**A:** Question recorded, but no automatic answer.

**Q:** What is the average price?

**A:** Means: {'order_id': 5.5, 'quantity': 3.6, 'price': 71.28}

**Q:** How many missing values are there in the dataset?

**A:** Total missing cells: 0
