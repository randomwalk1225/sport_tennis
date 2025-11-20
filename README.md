# 🎾 Tennis Match Predictor

AI-powered tennis match prediction system trained on 25 years of ATP data (2000-2024).

## Features

- **Predict match outcomes** between any ATP players
- **68.49% accuracy** using Gradient Boosting Classifier
- **671,389 matches** training dataset
- **Real player stats** from 2024 ATP data
- **Interactive web interface** built with Streamlit

## Live Demo

🔗 [Try it here!](#) _(Add your Streamlit Cloud URL after deployment)_

## Model Performance

| Metric | Value |
|--------|-------|
| Training Accuracy | 68.72% |
| Test Accuracy | 68.49% |
| Cross-Validation | 68.60% (±0.05%) |
| Dataset Size | 671,389 matches |
| Training Period | 2000-2024 (25 years) |

## Key Features Importance

1. **Ranking Difference**: 67.3%
2. **Player Age**: 15.3%
3. **Height**: 3.3%
4. **Surface & Tournament**: ~2%

## Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sportstat.git
cd sportstat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Project Structure

```
sportstat/
├── app.py                    # Streamlit web interface
├── head_to_head.py          # Match prediction logic
├── match_predictor.py       # ML model training
├── data_preprocessor.py     # Data preparation
├── data_manager.py          # Data loading utilities
├── models/
│   └── tennis_predictor_best.pkl  # Trained model
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

1. **Data Collection**: Loads historical ATP match data from Jeff Sackmann's tennis datasets
2. **Feature Engineering**: Extracts player rankings, age, height, surface preferences
3. **Model Training**: Gradient Boosting Classifier on 1.3M balanced samples
4. **Prediction**: Takes two player names, analyzes stats, predicts win probability

## Tech Stack

- **Python 3.13**
- **Streamlit** - Web framework
- **scikit-learn** - Machine learning
- **pandas** - Data processing
- **Playwright** - Web scraping (ATP Tour)

## Data Sources

- [Jeff Sackmann's Tennis Datasets](https://github.com/JeffSackmann/tennis_atp) (2000-2024)
- ATP Tour Player Activity (2022-2024)

## Model Details

**Algorithm**: Gradient Boosting Classifier
- 100 estimators
- Max depth: 5
- Learning rate: 0.1

**Training Process**:
1. Load 671,389 matches from 2000-2024
2. Create balanced dataset (2 samples per match)
3. Extract 14 key features
4. Train with 5-fold cross-validation
5. Save best model

## Contributing

Contributions welcome! Areas for improvement:
- Add WTA support
- Include head-to-head history
- Add recent form analysis
- Surface-specific statistics
- Live match tracking

## License

MIT License

## Author

Created with Claude Code

---

**Note**: This is a predictive model for entertainment purposes. Actual match outcomes depend on many factors not captured in historical data.
