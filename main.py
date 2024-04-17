import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import pandas as pd

st.set_page_config(layout="wide")

# SPLINE FOR EIR NUMBER
#---------------------------------------
# Function to plot the spline
def plot_spline(points, n_years):
    years = np.linspace(2025, 2025 + n_years - 1, num=3) # Adjust the years array based on n_years
    spline = CubicSpline(years, points)
    x_range = np.linspace(2025, 2025 + n_years - 1, 300)
    fig, ax = plt.subplots()
    ax.scatter(years, points, color='red', s=100, zorder=5, label='Adjustable Points')
    ax.plot(x_range, spline(x_range), label='Cubic Spline')
    ax.set_xlabel("Years")
    ax.set_ylabel("Number of EIR's per cohort (One cohort every 6 months)")
    ax.set_title("Set EIR's per cohort through interactive spline through points (Adjust on the left side)")
    ax.legend()
    ax.grid(True)
    plt.subplots_adjust(left=0.05, right=1.4) # Adjust these values as needed to stretch the plot horizontally
    return fig

st.markdown("""
    <div style="display: flex; align-items: center;">
        <img src="https://shorturl.at/esOV7" width="100">        
    </div>
    <h1> M E T A F O R G E </h1>
""", unsafe_allow_html=True)
st.markdown("#### _Financial model_")
st.markdown("<hr>", unsafe_allow_html=True)

n_years = st.sidebar.number_input("Number of years:", min_value=1, value=10, step=1)

st.subheader("Number of EIR's per cohort")
st.markdown("###### New cohorts starting every 6 months.")

col1, col2 = st.columns([4, 6])

with col1:
    with st.expander("EIR's per cohort ", expanded=True):
        mid_year = 2025 + (n_years - 1) / 2
        quarter_mid = 'Q' + str(2 if n_years % 2 == 0 else 3)
        quarter_end = 'Q4'
        label1 = f"EIR's at Q3 in year 2025"
        label2 = f"EIR's at {quarter_mid} in year {int(mid_year)}"
        label3 = f"EIR's at {quarter_end} in year {2025 + n_years - 1}"
        point1 = st.slider(label1, min_value=1, max_value=40, value=3)
        point2 = st.slider(label2, min_value=1, max_value=40, value=7)
        point3 = st.slider(label3, min_value=1, max_value=40, value=13)
        points = [point1, point2, point3]
        fig = plot_spline(points, n_years)

with col2:
    st.pyplot(fig)

def estimate_EIRs(month):
    # Assuming month 1 corresponds to January 2025
    target_year = 2025 + (month - 1) / 12
    # Ensure the spline has been initialized with the points from the latest sliders
    years = np.array([2025, 2025 + (n_years - 1) / 2, 2025 + n_years - 1])
    points = np.array([point1, point2, point3])
    spline = CubicSpline(years, points)
    # Get the estimate
    return spline(target_year)

# Prediction horizon
n_months = n_years * 12 
months = np.arange(1, n_months + 1)

# STAFF PROPORTIONS and SALARIES
# Slider widgets

with st.sidebar.expander("Proportionality factors", expanded=True):
    st.markdown('#### Proportionality factors')
    venture_builder_to_EIR = st.slider("Number of venture builders to EIR's", 0.1, 1.0, 0.5)
    admin_to_EIR = st.slider("Number of admin staff to EIR", 0.05, 0.5, 0.2)
    lab_costs_to_EIR = st.slider("Monthly lab costs per EIR in $k", 2, 50, 10) # in $k
    other_expenses_to_EIR = st.slider("Monthly other expenses per EIR (consultants, legal, misc. etc.) in $k ", 2, 80, 20) # in $k

with st.sidebar.expander("Monthly salaries", expanded=True):
    st.markdown('#### Monthly salaries')
    salary_admin = st.slider("Admin Staff ($k)", 3, 10, 6)
    salary_EIR = st.slider("EIRs ($k)", 10, 20, 13)
    salary_venture_builder = st.slider("Venture Builders ($k)", 10, 20, 13)
extended_months = n_months + 16  # Add 16 months (incubation + spinoff delay)

def new_cohort(n_EIR, starting_month,venture_builder_to_EIR, admin_to_EIR):
    # Initialize arrays for tracking staff and spinoffs

    n_EIR_cohort = np.zeros(extended_months)
    n_venture_builders_cohort = np.zeros(extended_months)
    n_admin_cohort = np.zeros(extended_months)
    n_spinoffs = np.zeros(extended_months)
    
    # Phase 1: EIR engagement
    duration_phase_1 = 2 # in months
    n_EIR_cohort[starting_month:starting_month + duration_phase_1] = n_EIR
    
    # Phase 2: Incubation period
    duration_incubation = 12 # in months
    fr_incubation = 0.7 # Fraction moving to incubation
    n_EIR_during_incubation = n_EIR * fr_incubation
    n_EIR_cohort[starting_month + duration_phase_1:starting_month + duration_phase_1 + duration_incubation] = n_EIR_during_incubation
    
    # Calculating spinoffs
    fr_spinoff = 0.5 # Fraction of incubations becoming spinoffs
    n_spinoffs[starting_month + duration_phase_1 + duration_incubation] = n_EIR_during_incubation * fr_spinoff
    
    return n_EIR_cohort, n_spinoffs

# Sum outputs from multiple cohorts
total_EIRs = np.zeros(extended_months)
total_spinoffs = np.zeros(extended_months)

# Simulate increasing number of cohorts over time
for i in range(int((n_months)/6)):
    starting_month = i * 6 # Starting a new cohort every half year
    n_EIR_cohort, n_spinoffs = new_cohort(estimate_EIRs(starting_month), starting_month, venture_builder_to_EIR, admin_to_EIR)
    total_EIRs += n_EIR_cohort
    total_spinoffs += n_spinoffs

venture_builders = total_EIRs*venture_builder_to_EIR
admin = total_EIRs*admin_to_EIR
lab_costs = total_EIRs*lab_costs_to_EIR
other_expenses= total_EIRs*other_expenses_to_EIR

# Ensuring that venture builder and admin staff stays up
for i in range(n_months):
    if i > 1:
        if venture_builders[i] < venture_builders[i-1]:
            venture_builders[i] = venture_builders[i-1]
            admin[i] = admin[i-1]

# Prepare data for plotting
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Expenses")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
ax1.plot(months, venture_builders[:n_months] * salary_venture_builder, label='Venture Builder Salaries')
ax1.plot(months, admin[:n_months] * salary_admin, label='Admin Salaries')
ax1.plot(months, total_EIRs[:n_months] * salary_EIR, label='EIR Salaries')
ax1.plot(months, lab_costs[:n_months], label='Lab costs')
ax1.plot(months, other_expenses[:n_months], label='Other expenses')

ax1.set_xlabel('Months')
ax1.set_ylabel('Individual expenses [$k]')
ax1.set_title('Monthly expenses, listed individually')
ax1.legend()

total_salaries = (venture_builders[:n_months] * salary_venture_builder) + (admin[:n_months] * salary_admin) + total_EIRs[:n_months] * salary_EIR + lab_costs[:n_months] + other_expenses[:n_months] 
ax2.plot(months, total_salaries, label='Total Monthly Expenses')
ax2.set_xlabel('Months')
ax2.set_ylabel('Total Expenses ($k)')
ax2.set_title('Total Monthly Salary Expenditure')
ax2.legend()

st.pyplot(fig)


st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Tabular format")

# Calculate the total salaries and reshape data for the table
quarters = months[::3][:n_years*4]  # Limit to the specified number of years
years = np.arange(2025, 2025 + len(quarters) // 4)
quarterly_expenses = np.add.reduceat(total_salaries, np.arange(0, len(total_salaries), 3))[:len(quarters)] / 3
quarterly_expenses = np.round(quarterly_expenses, -3) # Round to nearest thousand

# Ensure that the calculations don't produce decimals
quarterly_expenses = np.round(np.add.reduceat(total_salaries, np.arange(0, len(total_salaries), 3))[:len(quarters)] / 3, 0)
quarterly_venture_builders = np.round(np.add.reduceat(venture_builders, np.arange(0, len(venture_builders), 3))[:len(quarters)] / 3, 0)
quarterly_admin = np.round(np.add.reduceat(admin, np.arange(0, len(admin), 3))[:len(quarters)] / 3, 0)
quarterly_EIRs = np.round(np.add.reduceat(total_EIRs, np.arange(0, len(total_EIRs), 3))[:len(quarters)] / 3, 0)
quarterly_lab_costs = np.round(np.add.reduceat(lab_costs, np.arange(0, len(total_EIRs), 3))[:len(quarters)] / 3, 0)
quarterly_other_expenses = np.round(np.add.reduceat(other_expenses, np.arange(0, len(total_EIRs), 3))[:len(quarters)] / 3, 0)
quarterly_new_spinoffs = np.round(np.add.reduceat(total_spinoffs, np.arange(0, len(total_spinoffs), 3))[:len(quarters)], 0)
cumulative_spinoffs = np.round(np.cumsum(quarterly_new_spinoffs), 0)


#Creating DataFrame for display
data = {
'Year': np.repeat(years, 4)[:len(quarters)].astype(str), # Convert to string to avoid Arrow conversion issues
'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'] * len(years),
'Average Quarterly Expenses ($k)': quarterly_expenses.astype(int),
'Average Quarterly Venture Builders': quarterly_venture_builders.astype(int),
'Average Quarterly Admin Staff': quarterly_admin.astype(int),
'Average Quarterly EIRs': quarterly_EIRs.astype(int),
'Average Quarterly lab costs': quarterly_lab_costs.astype(int),
'Average Quarterly other expenses': quarterly_other_expenses.astype(int),
'New Spinoffs This Quarter': quarterly_new_spinoffs.astype(int),
'Spinoffs So Far (Cumulative)': cumulative_spinoffs.astype(int)
}

df = pd.DataFrame(data)

#Set the DataFrame index to 'Year' and 'Quarter' for better organization
df.set_index(['Year', 'Quarter'], inplace=True)

#Display using Streamlit 
st.dataframe(df)
