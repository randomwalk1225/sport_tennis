"""
Tennis Match Prediction Web App
Streamlit interface for predicting tennis match outcomes
"""

import streamlit as st
import pandas as pd
from head_to_head import HeadToHeadPredictor
import os

# Page configuration
st.set_page_config(
    page_title="Tennis Match Predictor",
    page_icon="🎾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-box {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .winner {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🎾 Tennis Match Predictor</div>', unsafe_allow_html=True)
st.markdown("### Predict match outcomes using AI trained on 25 years of ATP data (2000-2024)")

# Initialize predictor with caching
@st.cache_resource
def load_predictor():
    return HeadToHeadPredictor()

try:
    predictor = load_predictor()

    # Check if player data loaded successfully
    if predictor.player_data is None:
        st.error("Failed to load player database!")
        st.info("""
        **Troubleshooting:**
        - Make sure `players_database.json` exists in the repository
        - Check Streamlit Cloud logs for detailed errors
        - Try rebooting the app from Streamlit Cloud dashboard
        """)
        st.stop()

    # Get list of available players with rankings
    player_options = []
    for name, info in predictor.player_data.items():
        rank = int(info['rank']) if info['rank'] < 999 else 999
        if rank < 999:
            player_options.append(f"#{rank} - {name}")
        else:
            player_options.append(f"Unranked - {name}")

    player_options = sorted(player_options, key=lambda x: int(x.split(' - ')[0].replace('#', '').replace('Unranked', '9999')))

    st.success(f"[+] Model loaded! {len(player_options)} players in database")

    # Input section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Player 1")
        player1_selection = st.selectbox(
            "Select or search player:",
            options=[""] + player_options,
            key="player1",
            help="Type to search, or scroll to select",
            index=0
        )
        # Extract player name from selection
        player1_input = player1_selection.split(' - ')[-1] if player1_selection else ""

    with col2:
        st.subheader("Player 2")
        player2_selection = st.selectbox(
            "Select or search player:",
            options=[""] + player_options,
            key="player2",
            help="Type to search, or scroll to select",
            index=0
        )
        # Extract player name from selection
        player2_input = player2_selection.split(' - ')[-1] if player2_selection else ""

    # Match settings
    st.subheader("Match Settings")

    col3, col4, col5 = st.columns(3)

    with col3:
        surface = st.selectbox(
            "Court Surface:",
            ["hard", "clay", "grass"],
            help="Different surfaces affect play style"
        )

    with col4:
        is_grand_slam = st.checkbox("Grand Slam", help="Major tournament (longer matches)")

    with col5:
        is_masters = st.checkbox("Masters 1000", help="Top-tier tournament")

    # Predict button
    if st.button("🎾 Predict Match", type="primary", use_container_width=True):
        if player1_input and player2_input:
            with st.spinner("Analyzing match..."):
                result = predictor.predict_match(
                    player1_input,
                    player2_input,
                    surface=surface,
                    is_grand_slam=is_grand_slam,
                    is_masters=is_masters
                )

                if isinstance(result, str):
                    st.error(result)
                else:
                    # Display results
                    st.markdown("---")
                    st.markdown("## 📊 Prediction Results")

                    # Match info
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.info(f"**Court:** {result['surface'].upper()}")
                    with info_col2:
                        st.info(f"**Tournament:** {result['tournament_type']}")

                    # Player stats comparison
                    st.markdown("### Player Comparison")

                    comparison_data = {
                        "Metric": ["Ranking", "Age", "Height (cm)", "Hand"],
                        result['player1']['name']: [
                            f"#{int(result['player1']['rank'])}",
                            f"{result['player1']['age']:.1f}",
                            f"{result['player1']['height']:.0f}",
                            result['player1']['hand']
                        ],
                        result['player2']['name']: [
                            f"#{int(result['player2']['rank'])}",
                            f"{result['player2']['age']:.1f}",
                            f"{result['player2']['height']:.0f}",
                            result['player2']['hand']
                        ]
                    }

                    df_comparison = pd.DataFrame(comparison_data)
                    st.table(df_comparison)

                    # Win probabilities
                    st.markdown("### Win Probability")

                    prob_col1, prob_col2 = st.columns(2)

                    with prob_col1:
                        st.metric(
                            label=result['player1']['name'],
                            value=f"{result['p1_win_prob']:.2f}%",
                            delta=f"{result['p1_win_prob'] - 50:.2f}%"
                        )

                    with prob_col2:
                        st.metric(
                            label=result['player2']['name'],
                            value=f"{result['p2_win_prob']:.2f}%",
                            delta=f"{result['p2_win_prob'] - 50:.2f}%"
                        )

                    # Progress bars
                    st.progress(result['p1_win_prob'] / 100)

                    # Winner
                    st.markdown("### 🏆 Predicted Winner")
                    st.markdown(
                        f'<div class="winner">{result["predicted_winner"]}</div>',
                        unsafe_allow_html=True
                    )

                    # Analysis explanation
                    st.markdown("### 📋 Analysis")
                    for i, explanation in enumerate(result['explanation'], 1):
                        # Remove Korean text for now (encoding issues)
                        exp_clean = explanation.split(':')[0] if ':' in explanation else explanation
                        st.markdown(f"{i}. {exp_clean}")

        else:
            st.warning("Please enter both player names!")

    # Model information
    with st.expander("ℹ️ About this Model"):
        st.markdown("""
        **Model Details:**
        - **Algorithm:** Gradient Boosting Classifier
        - **Training Data:** 671,389 ATP matches (2000-2024)
        - **Accuracy:** 68.49% test accuracy
        - **Key Features:**
          - Ranking difference (67.3% importance)
          - Player age (15.3% importance)
          - Height difference (3.3% importance)
          - Court surface and tournament level

        **How it works:**
        The model analyzes historical match data to predict outcomes based on player statistics,
        court surface, and tournament importance. Rankings are the strongest predictor, but age,
        physical attributes, and playing conditions also matter.
        """)

    # Sample predictions
    with st.expander("🎯 Try Sample Predictions"):
        st.markdown("Popular matchups to try:")
        st.markdown("""
        - **#1 Novak Djokovic** vs **#2 Carlos Alcaraz**
        - **#4 Jannik Sinner** vs **#3 Daniil Medvedev**
        - **Rafael Nadal** vs **Roger Federer** (Legends)

        Use the dropdown menus above to select these players!
        """)

except Exception as e:
    st.error(f"Error loading predictor: {str(e)}")
    st.info("Make sure the model file exists at: models/tennis_predictor_best.pkl")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Tennis Match Predictor | Powered by 25 years of ATP data (2000-2024)</p>
    <p>Model: Gradient Boosting | Accuracy: 68.49%</p>
</div>
""", unsafe_allow_html=True)
