import streamlit as st
import pandas as pd
import joblib

# Loading model and dataset
model = joblib.load("app/credit_model.pkl")
df = pd.read_csv("app/credit_score_dataset.csv")
df['statename'] = df['statename'].str.lower()

# State encoding mapping
state_mapping = {
    'abia': 0, 'adamawa': 1, 'akwa ibom': 2, 'anambra': 3, 'bauchi': 4, 'bayelsa': 5, 'benue': 6, 'borno': 7,
    'cross river': 8, 'delta': 9, 'ebonyi': 10, 'edo': 11, 'ekiti': 12, 'enugu': 13, 'gombe': 14, 'imo': 15,
    'jigawa': 16, 'kaduna': 17, 'kano': 18, 'katsina': 19, 'kebbi': 20, 'kogi': 21, 'kwara': 22, 'lagos': 23,
    'nasarawa': 24, 'niger': 25, 'ogun': 26, 'ondo': 27, 'osun': 28, 'oyo': 29, 'plateau': 30, 'rivers': 31,
    'sokoto': 32, 'taraba': 33, 'yobe': 34, 'zamfara': 35
}

# Precomputing state-level averages for social/financial inclusion
state_avg_rates = df.groupby('statename')[
    ['borrowed_money_rate', 'cooperative_usage_rate', 'savings_group_usage_rate',
     'village_assoc_rate', 'thrift_usage_rate', 'social_group_rate']
].mean().to_dict(orient='index')

# Helper to fetch state-level averages
def get_state_averages(state_name):
    return state_avg_rates.get(state_name.lower(), {
        'borrowed_money_rate': 0.5,
        'cooperative_usage_rate': 0.5,
        'savings_group_usage_rate': 0.5,
        'village_assoc_rate': 0.5,
        'thrift_usage_rate': 0.5,
        'social_group_rate': 0.5
    })

# Streamlit config and styling
st.set_page_config(page_title="Creditworthiness Predictor", layout="centered")

st.markdown("""
    <style>
        .main {
            background-color: #e6ffe6;
        }
        .stButton>button {
            background-color: #008000;
            color: white;
            border-radius: 5px;
        }
        div[data-baseweb="select"] > div {
            background-color: #f0fff0 !important;
            color: black !important;
        }
        input[type="number"] {
            background-color: #f0fff0 !important;
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)


st.title("🏡 Creditworthiness Predictor")
st.markdown("### Please answer the following questions:")

# Creating the Form UI
with st.form("credit_form"):
    school_attd = st.selectbox("Did you attend high school?", ["Yes", "No"])

    edu_levels = {
        "None": 1,
        "Less than Primary": 2,
        "Primary": 3,
        "Junior Secondary": 4,
        "Senior Secondary": 5,
        "Tertiary/Post-Secondary": 6
    }
    edu_level_label = st.selectbox("What is your education level?", list(edu_levels.keys()))

    training = st.selectbox("Have you ever attended training?", ["Yes", "No"])
    training_type2 = st.selectbox("Have you received vocational training?", ["Yes", "No"])
    plots = st.number_input("How many plots do you have?", min_value=0, step=1)
    fishery = st.selectbox("Are you into fishery?", ["Yes", "No"])
    crops = st.number_input("How many different crops do you plant?", min_value=0, step=1)
    state = st.selectbox("What State is your farm situated in?", sorted(state_mapping.keys()))
    submit = st.form_submit_button("Predict Creditworthiness")

# code to Handle prediction
if submit:
    state_rates = get_state_averages(state)

    # Creating the input data
    data = {
        'hh_school_attd': 1 if school_attd == "Yes" else 0,
        'hh_edu_level': edu_levels[edu_level_label],
        'hh_trg': 1 if training == "Yes" else 0,
        'hh_trg_type__2': 1 if training_type2 == "Yes" else 0,
        'hh_plots_number': plots,
        'has_fishery': 1 if fishery == "Yes" else 0,
        'borrowed_money_rate': state_rates['borrowed_money_rate'],
        'cooperative_usage_rate': state_rates['cooperative_usage_rate'],
        'savings_group_usage_rate': state_rates['savings_group_usage_rate'],
        'village_assoc_rate': state_rates['village_assoc_rate'],
        'thrift_usage_rate': state_rates['thrift_usage_rate'],
        'social_group_rate': state_rates['social_group_rate'],
        'crop_diversity_score': crops,
        'statename_encoded': state_mapping[state],
        'statename': state_mapping[state]
    }

    # Converting to DataFrame
    input_df = pd.DataFrame([data])

    # Ensuring the feature order matches training
    expected_order = [
        'hh_school_attd', 'hh_edu_level', 'hh_trg', 'hh_trg_type__2',
        'hh_plots_number', 'has_fishery',
        'borrowed_money_rate', 'cooperative_usage_rate', 'savings_group_usage_rate',
        'village_assoc_rate', 'thrift_usage_rate', 'social_group_rate',
        'crop_diversity_score', 'statename_encoded', 'statename'
    ]
    input_df = input_df[expected_order]

    # Predict
    prediction = model.predict(input_df)[0]
    label = "Credible" if prediction == 1 else "At-Risk"

    if label == "Credible":
        st.success("🎉 Congratulations! You are eligible for the Credit Scheme.")
        st.markdown("Please call **+234 905 460 9925** or send \"Ready\" to **Creditforfarmers@gmail.com** to continue your application.")
    else:
        st.warning("⚠️ Sorry, you are not currently eligible for the credit scheme.")

        # 🧠 Offline Credit Advice Engine
        suggestions = []
        if edu_levels[edu_level_label] <= 3:
            suggestions.append("Consider enrolling in a literacy or vocational training program.")
        if training == "No":
            suggestions.append("Attending agricultural training can improve your productivity and eligibility.")
        if plots < 2:
            suggestions.append("Increasing the number of plots cultivated may boost your agricultural output.")
        if crops < 3:
            suggestions.append("Try to diversify your crops — planting 3 or more types improves resilience and income.")
        if fishery == "No":
            suggestions.append("Adding a secondary activity like fishery or livestock could increase your income streams.")
        if state_rates['social_group_rate'] < 0.05:
            suggestions.append("Join a local social or savings group in your area to strengthen your financial support network.")

        if suggestions:
            st.info("📘 Tips to Improve Your Creditworthiness:")
            for tip in suggestions:
                st.markdown(f"✅ {tip}")
        else:
            st.markdown("Keep working on your farm and stay active — your eligibility may improve soon.")
            st.markdown("[Watch Now: Improving Your Farm Credit Worthiness](https://www.youtube.com/watch?v=kP3-yV8BmVw&ab_channel=NCBA%27sCattlementoCattlemen)")
