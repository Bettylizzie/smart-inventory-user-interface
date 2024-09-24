import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import numpy as np

# Load dataset
st.title("Upload your dataset")

# File uploader to allow users to upload their dataset
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the uploaded Excel file
    data = pd.read_excel(uploaded_file)
    st.write("Data loaded successfully!")
    st.dataframe(data)
else:
    st.warning("Please upload an Excel file to proceed.")


# Custom Styles for Blue Menubar
st.markdown("""
    <style>
        .blue-menubar {
            background-color: #007bff;
            padding: 10px;
            font-size: 18px;
            font-weight: bold;
            color: white;
        }
        .dashboard-stat {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .notification {
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Admin Dashboard")  
options = st.sidebar.radio("Select a page:", (  
    "Dashboard",  
    "Inventory Monitoring",  
    "Sales Trends Analysis",  
    "User Settings",  
    "Reporting"  
))  

# Dashboard Overview Page  
if options == "Dashboard":  
    st.markdown('<div class="blue-menubar">Dashboard</div>', unsafe_allow_html=True)

    # Greeting message
    st.write("Hi Bettylizzie, here's the latest analysis of your inventory and sales.")

    # Alerts & Notifications
    st.subheader("Alerts & Notifications")
    if data['Stock levels'].min() < data['Reorder Levels'].min():
        st.markdown('<p class="notification">⚠ Low stock for some products. Please restock!</p>', unsafe_allow_html=True)
    else:
        st.success("No alerts currently. All stock levels are sufficient!")

    # Dashboard Statistics
    st.subheader("Dashboard Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="dashboard-stat"><h4>Total Products</h4><p>{}</p></div>'.format(data['Product Sold'].nunique()), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="dashboard-stat"><h4>Pending Reorders</h4><p>{}</p></div>'.format(data[data['Stock levels'] <= data['Reorder Levels']].shape[0]), unsafe_allow_html=True)

    # Charts for sales trends, predicted stocks, product PEI, and current stock levels
    st.subheader("Sales Trends")
    sales_data = data.groupby('Month')['Total Revenue'].sum().reset_index()
    st.line_chart(sales_data.set_index('Month'))

    st.subheader("Predicted Stocks")
    # Placeholder for prediction chart, you can replace this with your model's output
    st.line_chart(np.random.randint(50, 200, size=12))

    st.subheader("Product PEI")
    product_pei = data.groupby('Product Sold')['Profit'].mean().reset_index()
    st.bar_chart(product_pei.set_index('Product Sold'))

    st.subheader("Current Stock Levels")
    st.bar_chart(data[['Product Sold', 'Stock levels']].set_index('Product Sold'))

# Inventory Monitoring and Management Page  
elif options == "Inventory Monitoring":  
    st.title("📦 Inventory Monitoring")  
    st.write("Monitor and manage your inventory here.")

    # Filters for inventory view
    product_filter = st.selectbox("Filter by Product:", ['All'] + list(data['Product Sold'].unique()))
    location_filter = st.selectbox("Filter by Location:", ['All'] + list(data['Location'].unique()))

    # Apply filters
    filtered_data = data
    if product_filter != 'All':
        filtered_data = filtered_data[filtered_data['Product Sold'] == product_filter]
    if location_filter != 'All':
        filtered_data = filtered_data[filtered_data['Location'] == location_filter]

    st.dataframe(filtered_data[['Product Sold', 'Stock levels', 'Reorder Levels']])

    # Reorder Alerts
    st.subheader("⚠ Reorder Alerts")
    low_stock_items = filtered_data[filtered_data['Stock levels'] <= filtered_data['Reorder Levels']]
    if not low_stock_items.empty:  
        st.warning("Reorder Needed for the Following Items:")
        st.dataframe(low_stock_items[['Product Sold', 'Stock levels', 'Reorder Levels']])
    else:  
        st.success("All items are sufficiently stocked!")

    # Action form for stock updates
    st.write("### 🛠 Manage Inventory")
    product_to_update = st.selectbox("Select Product to Update:", data['Product Sold'].unique())
    new_stock = st.number_input("Update Stock Level:", min_value=0, value=int(data[data['Product Sold'] == product_to_update]['Stock levels'].values[0]))
    if st.button("Update Stock"):
        data.loc[data['Product Sold'] == product_to_update, 'Stock levels'] = new_stock
        st.success(f"Stock level for '{product_to_update}' updated to {new_stock}")

# Sales Data and Trend Analysis Page  
elif options == "Sales Trends Analysis":  
    st.title("📊 Sales Trends Analysis")  
    st.write("Analyze your sales trends over different seasons.")

    # Sales Trend by Season
    sales_seasonal = data.groupby('Season')['Total Revenue'].sum().reset_index()
    st.bar_chart(sales_seasonal.set_index('Season'))

    # Predictive Insights
    st.write("### 📉 Predictive Insights")
    st.write("These insights show expected stock needs based on trends.")
    # Placeholder for predictive analytics
    st.line_chart(np.random.randint(50, 200, size=12))

# User Settings Page  
elif options == "User Settings":  
    st.title("⚙ User Settings")
    st.write("Manage user settings and permissions.")

    st.write("### Adjust Stock Thresholds")
    threshold = st.number_input("Set Global Reorder Threshold:", min_value=0, value=10)
    if st.button("Set Threshold"):
        data['Reorder Levels'] = threshold
        st.success(f"Global reorder threshold set to {threshold}.")

    st.write("### User Roles")
    role = st.selectbox("Select Role for User:", ["Manager", "Employee"])
    st.write(f"Assigned role: {role}")

# Reporting Page  
elif options == "Reporting":  
    st.title("📑 Reporting")
    st.write("Generate and export reports.")

    report_type = st.selectbox("Select Report Type:", ["Monthly Sales", "Inventory Performance", "Predictive Insights"])
    if st.button("Generate Report"):
        st.success(f"{report_type} Report generated!")
