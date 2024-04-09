import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Function definitions
def calculate_holdings_value(MA_share_post_conversion, staff_incentivisation, convertible_shares_frac, frac_convertible_from_MA):
    return (MA_share_post_conversion * (1 - staff_incentivisation / 100)) + frac_convertible_from_MA * 100 * convertible_shares_frac

def plot_portfolio(MA_share_val, staff_incentivisation_val, convertible_investment_val, frac_convertible_from_MA_val, pre_money_valuation_val, convertible_cap_val, MA_premoney_val, annual_spinoffs_vals):
    convertible_shares_frac = convertible_investment_val / min(convertible_cap_val, pre_money_valuation_val)
    holdings_values = []
    total_money_spent_on_convertibles = 0
    total_spinoffs = 0

    for year, spinoff_count in annual_spinoffs_vals.items():
        total_spinoffs += spinoff_count
        future_value = total_spinoffs * calculate_holdings_value(MA_share_val, staff_incentivisation_val, convertible_shares_frac, frac_convertible_from_MA_val) * pre_money_valuation_val / 100
        holdings_values.append(future_value / 1e6)
        total_money_spent_on_convertibles += spinoff_count * convertible_investment_val * frac_convertible_from_MA_val

    portfolio_value_2030 = sum(holdings_values)
    VC_ownership_in_MA = total_money_spent_on_convertibles / (MA_premoney_val + total_money_spent_on_convertibles)
    ROI = portfolio_value_2030 * VC_ownership_in_MA / total_money_spent_on_convertibles * 1e6

    fig, ax = plt.subplots()
    ax.bar(annual_spinoffs_vals.keys(), np.cumsum(list(holdings_values)))
    ax.set_xlabel('Year')
    ax.set_title('Cumulative Portfolio value in USD M')
    st.pyplot(fig)
    
    return total_money_spent_on_convertibles, portfolio_value_2030, VC_ownership_in_MA, ROI

# Streamlit UI layout
st.title('Why invest in MetaAnvil')

disclaimer = """
----
### Note
The model assumes that we take all money up to 2030 in right now. Splitting this up into multiple financing rounds will improve things tremendously. The fact that the ROI looks decent despite not having modeled for this already says a lot about the viability of MetaAnvil's incubation.
<br><br><br>
"""

st.markdown(disclaimer, unsafe_allow_html=True)


# Define the default values for sliders
MA_share_val_default = 24
staff_incentivisation_val_default = 30
convertible_investment_val_default = 0.8 * 1e6
frac_convertible_from_MA_val_default = 0.3
pre_money_valuation_val_default = 10 * 1e6
convertible_cap_val_default = 5 * 1e6
MA_premoney_val_default = 10 * 1e6
years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
default_spinoffs = [2, 1, 3,4, 6, 9, 13, 18]
annual_spinoffs_vals = {year: default_spinoffs[i] for i, year in enumerate(years)}

# Define the layout for sliders
col1, col2 = st.columns(2)

# Function to calculate convertible_shares_frac
def calculate_convertible_shares_frac(convertible_investment, convertible_cap, pre_money_valuation):
    return convertible_investment / min(convertible_cap, pre_money_valuation)

# Define sliders in columns
with col1:
    with st.expander("MetaAnvil and Staff Incentives", expanded=False):
        MA_share_val = st.slider('MetaAnvil shares at spinoff [%] (excl convertible share)', 0, 35, MA_share_val_default)
        staff_incentivisation_val = st.slider('% of MA\'s share being used to incentivize staff', 15, 40, staff_incentivisation_val_default)        
        # Calculate convertible_shares_frac for use here
        convertible_shares_frac_temp = calculate_convertible_shares_frac(convertible_investment_val_default, convertible_cap_val_default, pre_money_valuation_val_default)
        convertible_share = convertible_shares_frac_temp * frac_convertible_from_MA_val_default * 100
        convertible_share_text = f"""
        {convertible_share:.2f}% <br> Shares from MetaAnvil's part in the convertible
        """
        st.markdown(convertible_share_text, unsafe_allow_html=True)
        
    with st.expander("MetaAnvil Valuation", expanded=False):
            MA_premoney_val = st.slider('MetaAnvil pre-money valuation in USD M', 5, 25, int(MA_premoney_val_default / 1e6), step=1) * 1e6
            
    with st.expander("Convertible Notes and Spinoff Valuations", expanded=False):
        convertible_investment_val = st.slider('Avg. convertible sum in USD M', 0.1, 1.0, convertible_investment_val_default / 1e6, step=0.1) * 1e6
        frac_convertible_from_MA_val = st.slider('Fraction of convertible from MA [%]', 10, 50, int(frac_convertible_from_MA_val_default * 100), step=1) / 100
        pre_money_valuation_val = st.slider('Avg. pre-money in USD M', 5, 20, int(pre_money_valuation_val_default / 1e6), step=1) * 1e6
        convertible_cap_val = st.slider('Convertible cap in USD M', 5, 9, int(convertible_cap_val_default / 1e6), step=1) * 1e6
        # Calculate and use convertible_shares_frac here
        convertible_shares_frac = calculate_convertible_shares_frac(convertible_investment_val, convertible_cap_val, pre_money_valuation_val)

with col2:    

    with st.expander("Annual Spinoffs", expanded=False):
        for i, year in enumerate(years):
            annual_spinoffs_vals[year] = st.slider(f'Spinoffs of {year}', 1, 18, default_spinoffs[i], key=f'spinoff_{year}_{i}')

    with st.expander("", expanded=False):
        st.markdown("", unsafe_allow_html=True)
    with st.expander("", expanded=False): 
        st.markdown("", unsafe_allow_html=True)

# Call the plot function to update plot and values dynamically
total_money_spent, portfolio_value_2030, VC_ownership, ROI = plot_portfolio(
    MA_share_val, staff_incentivisation_val, convertible_investment_val, 
    frac_convertible_from_MA_val, pre_money_valuation_val, convertible_cap_val, 
    MA_premoney_val, annual_spinoffs_vals
)

# Display financial metrics right below the plot
financial_metrics = f"""
----
<div style='font-size: 34px; font-weight: bold;'>
    ROI = {ROI:.2f}x<br>    
</div>
<div style='font-size: 24px;'>    
    Total funding = {total_money_spent/1e6:.1f} M<br>
    Value of MetaAnvil's Portfolio in 2030 = {portfolio_value_2030:.0f} M<br>
    VC ownership of MA = {VC_ownership*100:.0f} %<br><br>
</div>
"""
st.markdown(financial_metrics, unsafe_allow_html=True)

why_MetaAnvil = f"""
----
## Intent 

- Demonstrate why the ROI of funding MetaAnvil is higher than funding individual spinoffs directly.
- Highlight that MetaAnvil as an incubator is a VC case, based on assumptions verified by its most recent spinoff Astrobeam.


### Hypotheses

- MetaAnvil can keep consistently created high-value spinoff.
- MetaAnvil cash-efficiently crates enough value to justify a decent bite without tripping up the spinoffs in future rounds.
- With funding MetaAnvil can streamline its activities to bring down incubation costs, durations, while increasing the market readiness of spinoffs.

### The Astrobeam Spinoff Example

Astrobeam received a ~ 0.5M convertible investment notes from a VC, with a 5M cap. Astrobeam subcontracted MetaAnvil to act as de-facto founders, who e.g. performed user interviews and formed partnerships, analysed competitor tech, created system designs, initial specs, metasurface designs, patentable IP, established supplier relationships, pre-negotiated FTO agreements, assembled a team of industry leading consultants, handled marketing, and found an experienced photonics CEO/founder to take over. The new CEO was very happy with the value that MetaAnvil provided, and agreed to have MetaAnvil own 24% of Astrobeam, while the convertible note share will be determined upon Astrobeam’s next qualified round.

### Further increasing spinoff efficiency

- De-risk cheap, find out early whether we want to drop something. Keep the fraction of person-hours flowing into dead-ends under ⅓.
- Get spinoff CEO to join early. Reduces spinoff team risk, handoff friction. Part of MetaAnvil’s spinoff shares that would have incentivised our own incubation manager goes to CEO instead to keep the part of the share that goes to our holdings constant.
- Shared resources (software, expertise etc) will bring the value provided to startups up at no extra cost to us.
- Use our growing reputation and network of industry specialists to get introductions to CEO’s of industry leading users.
- Use MetaAnvil’s access to classified need of US government agencies and relationships to decision makers who are eager to have metamaterial prodcuts, to bid for contracts in which we designate our spinoffs and the spinoff’s customers as major subcontractor (DARPA, Air Force, Space Force, NASA). 

### Use of Funds

Fund our own incubations. More successful spinoffs per $. Being able to quickly tweak spend and strategy (dropping something or doubling down on it) lets us:

- Cut the spinoff timeline in half by avoiding pauses and constant fundraising.
- MetaAnvil founders and spinoff CEO’s spend less time on bureaucracy, and more time de-risking.
- Higher ROI: Generate a higher increase in portfolio value per invested dollar compared to betting on a single incubation. Allows us to move resources from sub-optimal incubations to star candidates.
- More cost-effective de-risking through shared resources: Simulation software, engineers, expertise, network. Increase ratio of person-hours worked by employees over contractors. Allows us to further improve our proprietary and peerless simulation software to further increase the unfair advantage of our spinoffs with faster design and manufacturing.
- More time-efficient capital deployment. Being pitched to for every $200k delays getting your funds to work.

### Strategy

According to the above model, carrying the full convertible note amount ourselves (and reaping that additional portion of the spinoff equity) actually significantly brings down MetaAnvil’s ROI.

The reason for this is that MetaAnvil creates a massive ROI through the roughly 24% that receives for its incubation efforts, which is significantly higher than the ~2x return that the convertible note delivers when converting with the 5M cap on a 10M pre-money valuation of the spinoff. However, un-bureaucratically covering some of these convertibles ourselves helps streamline the incubation activity that has such a large lever on the ROI.

When the industry focus and stage of an incubation overlaps with the needs of an external party, such as a VC or a university (several of which are already very interested) that is willing to act fast, MetaAnvil is incentivised to have them provide the convertible or SAFE.

When none of our funding partners is in a position to make a quick decision, MetaAnvil can step in with cash, provide up to several hundred thousand into startups that it naturally knows most about, and allow MetaAnvil’s entrepreneurs or spinoff CEO’s to spend more time building before having to start diverting time to fundraising. The ability to easily bridge gaps between convertible notes prevents project pauses, without which the Astrobeam incubation for instance would have only taken half the time.

"""
with st.expander("Why MetaAnvil", expanded=True):
    st.markdown(why_MetaAnvil, unsafe_allow_html=True)

why_the_world_needs_metamaterials = f"""
----
# Why the World Needs Metamaterials

## What are Metamaterials?
Metamaterials (mmats) are materials characterized by their unique pattern of unit-cells, not by a new chemical makeup. These patterns allow metamaterials to shape and steer electromagnetic beams without moving parts, often made up of a flat, two-dimensional array of repeating cells.

## Metamaterial Advantages

- **Create Arbitrary Beam Shapes On The Fly**
  - Access to exotic, efficient search patterns, improving wireless communication, radar performance, through-wall imaging, etc.
  - Focused RF beams enhance signal strength and reduce interference, maximizing bandwidth utilization.
- **Change Beam Direction Instantly**
  - Eliminates dead-times in inter-satellite laser communication.
  - Enables laser-based point-to-multipoint connections by quickly alternating between communication partners.
- **Reduced Interference/Jamming**
  - Beamforming minimizes signal clash, enhancing network resilience (e.g., Starlink in Ukraine).
- **Stealth**
  - Focused beams make source detection difficult, safeguarding locations (e.g., in military applications).
  - Proximity required to detect transmissions, enhancing operational secrecy.
  - Empowers F-35s with advanced radar capabilities without location disclosure.
- **Longer Range**
  - Enhanced focus in transmission extends the range, crucial for mobile platforms.
- **No Moving Parts**
  - Increases reliability, reduces maintenance costs.
  - Resilient to high accelerations, temperature variations, and vibrations.
  - Minimizes performance impact on other equipment.
- **Insensitivity to Vibrations**
  - High-frequency steering immune to mechanical vibrations.
- **Remote Upgradability**
  - Reconfigurable to emulate various antenna characteristics.
- **Fault Tolerance**
  - Modular design allows for resilience against component failures.
- **Interoperability**
  - Easily integrates with various systems due to software-based control.
- **Energy Efficiency**
  - Direct result of focused tracking capability.
- **Low Latency**
  - Rapid adjustments reduce data transmission delays.
- **Spectral Efficiency**
  - Enhanced frequency spectrum utilization for increased data transmission.
- **Lower Cost**
  - Mass producible using existing fabrication technologies.
- **Smaller Elements and Lighter, Thinner Design**
  - High density of unit cells enables precise beam shaping.
- **Self-Calibratable**
  - Compensates for manufacturing defects, allowing higher tolerances.
- **Conformable Shapes**
  - Adaptable to various surface geometries, enhancing application in diverse fields.

*Note: Phased array approaches, though somewhat similar, are larger, heavier, more power-consuming, and significantly more expensive than metamaterials. They are also less flexible in shaping beams and cannot be easily conformed to varied shapes.*

"""
with st.expander("The world needs metamaterials", expanded=False):
    st.markdown(why_the_world_needs_metamaterials, unsafe_allow_html=True)
