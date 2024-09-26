import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt  
import numpy as np
import hashlib
from fpdf import FPDF  # For PDF report
import os

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if user exists
def check_user_exists(username, users_db):
    return username in users_db

# Function for the login page
def login_page(users_db):
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users_db:
            hashed_password = users_db[username]['password']
            if hash_password(password) == hashed_password:
                st.success(f"Welcome {username}!")
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = username
                st.session_state['user_role'] = users_db[username].get('role', 'Employee')  # Default to Employee if no role
                if 'dataset' in users_db[username]:
                    st.session_state['data'] = users_db[username]['dataset']
                    st.success("Loaded your previously uploaded dataset.")
            else:
                st.error("Incorrect password.")
        else:
            st.error("User does not exist. Please sign up.")

# Function for the signup page
def signup_page(users_db):
    st.subheader("Sign Up")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Role", ["Manager", "Employee"])

    if st.button("Sign Up"):
        if new_username in users_db:
            st.error("Username already taken. Please choose another.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Store hashed password and role in database
            users_db[new_username] = {'password': hash_password(new_password), 'role': role}
            st.success("Account created successfully! Please log in.")
            st.session_state['users_db'] = users_db

# Initialize session state if not already done
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Main app flow
if st.session_state['logged_in']:
    st.write(f"Welcome, {st.session_state['current_user']}!")
    
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state.pop('data', None)
        st.experimental_rerun()

else:
    # Prevent access to the system without login
    page_choice = st.selectbox("Choose a page", ["Login", "Sign Up"])
    if page_choice == "Login":
        login_page(st.session_state['users_db'])
    else:
        signup_page(st.session_state['users_db'])

# Dataset upload and other pages (only accessible after login)
if st.session_state['logged_in']:
    # Sidebar for navigation
    st.sidebar.title("Admin Dashboard")  
    options = st.sidebar.radio("Select a page:", (  
        "Upload Dataset",  
        "Dashboard",  
        "Inventory Monitoring",  
        "Sales Trends Analysis",  
        "User Settings",  
        "Reporting"  
    ))  

    # Upload Dataset page (only if user is logged in)
    if options == "Upload Dataset":  
        st.title("Upload your dataset")
        uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

        if uploaded_file is not None:
            st.session_state['data'] = pd.read_excel(uploaded_file)
            st.session_state['users_db'][st.session_state['current_user']]['dataset'] = st.session_state['data']  # Save dataset for the user
            st.success("Data loaded successfully!")
            st.dataframe(st.session_state['data'])
        else:
            st.warning("Please upload an Excel file to proceed.")

# Proceed to other pages if dataset is already loaded in session state
if 'data' in st.session_state and st.session_state['data'] is not None:
    data = st.session_state['data']  # Get the dataset from session state


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

    # Dashboard Overview Page  
    if options == "Dashboard":  
        st.markdown('<div class="blue-menubar">Dashboard</div>', unsafe_allow_html=True)

        # Greeting message
        st.write(f"Hi {st.session_state['current_user']}, here's the latest analysis of your inventory and sales.")

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
        st.line_chart(np.random.randint(50, 200, size=12))

        st.subheader("Profit per product")
        product_pei = data.groupby('Product Sold')['Profit'].mean().reset_index()
        st.bar_chart(product_pei.set_index('Product Sold'))

        st.subheader("Current Stock Levels")
        st.bar_chart(data[['Product Sold', 'Stock levels']].set_index('Product Sold'))

    # Inventory Monitoring and Management Page  
    if options == "Inventory Monitoring":  
        st.title("📦 Inventory Monitoring")  
        st.write("Monitor and manage your inventory here.")

        # Filters for inventory view
        product_filter = st.selectbox("Filter by Product:", ['All'] + list(data['Product Sold'].unique()))
        location_filter = st.selectbox("Filter by Location:", ['All'] + list(data['Location'].unique()))
        reorder_filter = st.checkbox("Show only products below reorder level")

        # Apply filters independently
        filtered_data = data
        if product_filter != 'All':
            filtered_data = filtered_data[filtered_data['Product Sold'] == product_filter]
        if location_filter != 'All':
            filtered_data = filtered_data[filtered_data['Location'] == location_filter]

        # Show filtered inventory
        st.dataframe(filtered_data[['Product Sold', 'Location', 'Stock levels', 'Reorder Levels']])

        # Reorder Alerts (independent filter)
        st.subheader("⚠ Reorder Alerts")
        if reorder_filter:
            low_stock_items = filtered_data[filtered_data['Stock levels'] <= filtered_data['Reorder Levels']]
            if not low_stock_items.empty:
                st.warning("Reorder Needed for the Following Items:")
                st.dataframe(low_stock_items[['Product Sold', 'Location', 'Stock levels', 'Reorder Levels']])
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

     # Ensure you have the necessary imports

# Create a directory for storing data if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# User Settings Page
elif options == "User Settings":
    st.title("⚙ User Settings")
    st.write("Manage user-specific settings and thresholds here.")

    # Stock threshold adjustment
    new_reorder_level = st.number_input("Set new reorder threshold level:", min_value=1)
    if st.button("Update Reorder Level"):
        data['Reorder Levels'] = new_reorder_level
        st.success(f"Reorder level updated to {new_reorder_level} for all products")

    # Manage product categories
    st.write("### Manage Product Categories")
    categories = st.text_input("Enter product categories (comma-separated):")
    if st.button("Save Categories"):
        if categories:
            # Save categories to a persistent location in the 'data' folder
            with open("data/categories.txt", "w") as f:
                f.write(categories)
            st.success("Product categories saved successfully.")
        else:
            st.error("Please enter valid categories.")

    # Add new product to stock
    st.write("### Add New Product")
    product_name = st.text_input("Product Name:")
    quantity = st.number_input("Quantity:", min_value=1)
    price = st.number_input("Price per Product:", min_value=0.0)
    
    if st.button("Add Product"):
        if product_name and quantity > 0 and price >= 0:
            new_product = {
                "Product Sold": product_name,
                "quantity sold": quantity,
                "Total Revenue": quantity * price,
                "Location": "Default Location"  # or any default you want
            }
            # Append new product to data
            data = pd.concat([data, pd.DataFrame([new_product])], ignore_index=True)
            st.success(f"Product '{product_name}' added successfully.")
        else:
            st.error("Please fill in all fields correctly.")

    # Save updated data to a persistent location in the 'data' folder
    data.to_csv("data/inventory_data.csv", index=False)  # Update to use the 'data' folder


# Reporting Page
if options == "Reporting":
    st.title("📑 Reporting")
        
    # Generate reports
    st.write("### Generate Sales Report")
    report_type = st.selectbox("Select Report Type", ["Monthly", "Seasonal", "Yearly", "Inventory Performance"])

    if st.button("Generate Report"):
        # Group and summarize data based on report type
        if report_type == "Monthly":
            data['Month'] = pd.to_datetime(data['Month'], errors='coerce').dt.month_name()
            sales_summary = data.groupby(['Month', 'Location']).agg({
                'Total Revenue': 'sum',
                'quantity sold': 'sum',
                'Product Sold': 'count'
            }).reset_index()

        elif report_type == "Seasonal":
            # Ensure the 'Season' column has values before aggregating
            sales_summary = data.groupby(['Season', 'Location']).agg({
                'Total Revenue': 'sum',
                'quantity sold': 'sum',
                'Product Sold': 'count'
                }).reset_index()

        elif report_type == "Yearly":
            st.write("### 📅 Yearly Sales Report")
            sales_summary = pd.DataFrame({
                'Year': [2023, 2024],
                'Total Revenue': data['Total Revenue'].sum() * 1.05
            })

        elif report_type == "Inventory Performance":
            st.write("### Inventory Performance Report")
            sales_summary = data.groupby(['Product Sold']).agg({
                'quantity sold': 'sum',
                'Total Revenue': 'sum'
            }).reset_index()

        # Sort the report by 'Total Revenue' in descending order
        sales_summary = sales_summary.sort_values(by='Total Revenue', ascending=False)
        
        # Display the report (once)
        st.dataframe(sales_summary)

        # CSV download
        csv_data = sales_summary.to_csv(index=False).encode('utf-8')

        # Download as PDF
        if st.button("Download Report as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add title
            pdf.cell(200, 10, txt=f"{report_type} Sales Report", ln=True, align='C')

            # Add table headers
            for col in sales_summary.columns:
                pdf.cell(40, 10, col, 1)
            pdf.ln()

            # Add table data
            for i in range(len(sales_summary)):
                for col in sales_summary.columns:
                    pdf.cell(40, 10, str(sales_summary[col].iloc[i]), 1)
                pdf.ln()

            pdf_file_path = f"{report_type}_sales_report.pdf"
            pdf.output(pdf_file_path)

            with open(pdf_file_path, "rb") as f:
                st.download_button(
                    label="Download Report as PDF",
                    data=f,
                    file_name=pdf_file_path,
                    mime='application/pdf'
                )    
        # Recommendation
        st.write("### Recommendations")
         # General recommendation for balancing products
        st.info("To balance product performance:")
        st.write("- Analyze sales trends to identify high-performing product categories.")
        st.write("- Allocate marketing resources accordingly to boost sales for underperforming categories.")
        st.write("- Regularly review inventory to avoid overstocking products with low demand.")

