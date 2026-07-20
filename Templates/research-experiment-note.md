---
title: "[EXP-YYYY-XXX] Experiment Name"
theme: "your-research-theme"
type: "experiment"
status: "in-progress"
experiment_id: "EXP-YYYY-XXX"
objective: "実験の目的"
hypothesis: "仮説"
reproducible: true
resource_consumed: "GPU: 8xA100, Memory: 256GB, Time: 12h"
github_link: ""
tags: ["experiment", "llm", "reproducible"]
created: "{{DATE:YYYY-MM-DD}}"
updated: "{{DATE:YYYY-MM-DD}}"
---

# [EXP-YYYY-XXX] Experiment Name

**Date**: {{DATE:YYYY-MM-DD}}  
**Experiment ID**: EXP-YYYY-XXX  
**Status**: In Progress

---

## 🎯 Objective

*実験の明確な目的を記述*

---

## 🔍 Hypothesis

*検証したい仮説*

---

## 🛠️ Methodology

### Experiment Design
- 

### Dataset
- **Name**: 
- **Size**: 
- **Source**: 

### Model/Method
- **Architecture**: 
- **Version**: 
- **Parameters**: 

### Hyperparameters
```python
{
  "learning_rate": 0.001,
  "batch_size": 32,
  "epochs": 10,
  "seed": 42
}
```

### Experimental Setup
- **Hardware**: GPU: 8xA100, CPU: XXX cores
- **Software**: Python 3.11, PyTorch 2.0, CUDA 12.1
- **Framework**: 
- **Time**: 12 hours

---

## 📊 Results

### Key Metrics
| Metric | Value | Baseline | Improvement |
|--------|-------|----------|-------------|
| Accuracy | XX.XX% | XX.XX% | +X.XX% |
| Loss | X.XXX | X.XXX | -X.XXX |

### Detailed Results
- 

### Visualization
[グラフ・図表をここに埋め込み]

---

## 🔎 Analysis

### What Worked Well
- 

### Unexpected Findings
- 

### Interpretation
- 

---

## ⚠️ Limitations

- 

---

## 🔄 Reproducibility Checklist

- [ ] Random seed is fixed
- [ ] Hyperparameters are documented
- [ ] Dataset is versioned
- [ ] Code is in version control: [GitHub Link]
- [ ] Environment is reproducible: [pyproject.toml / uv.lock]

### How to Reproduce
```bash
# Step 1: Setup
uv run python setup.py

# Step 2: Run experiment
uv run python experiments/EXP-YYYY-XXX.py --seed 42

# Step 3: Evaluate
uv run python evaluate.py --model_path results/EXP-YYYY-XXX/model.pt
```

---

## 📚 Related Papers & Experiments

- Related paper: （実在する paper note への wikilink）
- Follow-up experiment: （実在する experiment note への wikilink）

---

## 💭 Next Steps

- [ ] 
- [ ] 
- [ ] 

---

## 📝 Appendix

### Additional Analysis
- 

### Raw Data & Logs
- **Logs**: `results/EXP-YYYY-XXX/logs/`
- **Checkpoints**: `results/EXP-YYYY-XXX/checkpoints/`

---

*Experiment conducted: {{DATE:YYYY-MM-DD}}*  
*Last Updated: {{DATE:YYYY-MM-DD}}*
