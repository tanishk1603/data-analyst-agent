# Data Analyst Agent — Report

## Profile
- Rows: **5**
- Columns: **6**
- Duplicates: **0**
- Memory: **0.001 MB**

### Dtypes

- `EmployeeID`: int64
- `Name`: object
- `Age`: int64
- `Department`: object
- `Salary`: int64
- `YearsAtCompany`: int64

### Missing by Column

- `EmployeeID`: 0
- `Name`: 0
- `Age`: 0
- `Department`: 0
- `Salary`: 0
- `YearsAtCompany`: 0

## Summary Statistics

```json
{
  "EmployeeID": {
    "count": 5.0,
    "mean": 3.0,
    "std": 1.5811388300841898,
    "min": 1.0,
    "25%": 2.0,
    "50%": 3.0,
    "75%": 4.0,
    "max": 5.0
  },
  "Age": {
    "count": 5.0,
    "mean": 35.0,
    "std": 7.905694150420948,
    "min": 25.0,
    "25%": 30.0,
    "50%": 35.0,
    "75%": 40.0,
    "max": 45.0
  },
  "Salary": {
    "count": 5.0,
    "mean": 70000.0,
    "std": 15811.388300841896,
    "min": 50000.0,
    "25%": 60000.0,
    "50%": 70000.0,
    "75%": 80000.0,
    "max": 90000.0
  },
  "YearsAtCompany": {
    "count": 5.0,
    "mean": 5.0,
    "std": 3.1622776601683795,
    "min": 1.0,
    "25%": 3.0,
    "50%": 5.0,
    "75%": 7.0,
    "max": 9.0
  }
}
```

## Correlations/Associations

![Pearson Heatmap](/outputs/20250817-160233-1e746f49/corr_heatmap.png)
### Spearman top pairs
- EmployeeID ↔ Age: 1.000
- EmployeeID ↔ Salary: 1.000
- EmployeeID ↔ YearsAtCompany: 1.000
- Age ↔ Salary: 1.000
- Age ↔ YearsAtCompany: 1.000
- Salary ↔ YearsAtCompany: 1.000
### Categorical association (heuristic)
- Name ↔ Department: score=0.200

## Visuals

![hist_EmployeeID.png](/outputs/20250817-160233-1e746f49/hist_EmployeeID.png)
![box_EmployeeID.png](/outputs/20250817-160233-1e746f49/box_EmployeeID.png)
![hist_Age.png](/outputs/20250817-160233-1e746f49/hist_Age.png)
![box_Age.png](/outputs/20250817-160233-1e746f49/box_Age.png)
![hist_Salary.png](/outputs/20250817-160233-1e746f49/hist_Salary.png)
![box_Salary.png](/outputs/20250817-160233-1e746f49/box_Salary.png)
![hist_YearsAtCompany.png](/outputs/20250817-160233-1e746f49/hist_YearsAtCompany.png)
![box_YearsAtCompany.png](/outputs/20250817-160233-1e746f49/box_YearsAtCompany.png)
![bar_Name.png](/outputs/20250817-160233-1e746f49/bar_Name.png)
![bar_Department.png](/outputs/20250817-160233-1e746f49/bar_Department.png)

## Answers

**Q:** 1. What is the average salary of employees?

**A:** Means: {'EmployeeID': 3.0, 'Age': 35.0, 'Salary': 70000.0, 'YearsAtCompany': 5.0}

**Q:** 2. Which department has the highest average age?

**A:** Means: {'EmployeeID': 3.0, 'Age': 35.0, 'Salary': 70000.0, 'YearsAtCompany': 5.0}

**Q:** 3. How many employees work in the IT department?

**A:** Question recorded, but no automatic answer.

**Q:** 4. Who is the youngest employee?

**A:** Question recorded, but no automatic answer.

**Q:** 5. Give me a summary of years at the company.

**A:** Question recorded, but no automatic answer.
