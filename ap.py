import streamlit as st
import pandas as pd
import itertools
import time

# Provided Topics and Descriptions
topics_data = [
    {"Topic": "Python Data Types and Variables", "Description": "Lists, Tuples, Sets, Dictionaries"},
    {"Topic": "Control Flow in Python", "Description": "Conditional statements (if-else), loops (for, while)"},
    {"Topic": "Functions in Python", "Description": "Defining and calling functions, arguments, return values"},
    {"Topic": "File Handling in Python", "Description": "Reading and writing files (open(), read(), write())"},
    {"Topic": "Exception Handling", "Description": "try, except, finally"},
    {"Topic": "Higher-Order Functions", "Description": "map(), filter(), reduce()"},
    {"Topic": "Object-Oriented Programming (OOP)", "Description": "OOP concepts"},
]

@st.cache_data
def load_data(file_path):
    time.sleep(0.5)  # Reduced to 0.5 seconds for faster loading
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    
    required_columns = {'name', 'marks'}
    if not required_columns.issubset(df.columns):
        st.error(f"Missing columns: {required_columns - set(df.columns)}. Ensure your CSV has 'Name' and 'Marks'.")
        return None
    
    df_filtered = df[['name', 'marks']].copy()
    df_filtered.rename(columns={'name': 'Name', 'marks': 'Marks'}, inplace=True)
    return df_filtered[['Name', 'Marks']]

def categorize_students(data):
    time.sleep(0.5)  # Reduced to 0.5 seconds
    data['Category'] = pd.cut(data['Marks'], bins=[-1, 25, 35, 100], labels=['<25', '25-35', '>35'])
    return data

def create_custom_batches(data):
    time.sleep(1)  # Reduced to 1 second
    grouped_batches = []
    shuffled_data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    high = shuffled_data[shuffled_data['Category'] == '>35']  # 1 per batch
    mid = shuffled_data[shuffled_data['Category'] == '25-35']  # 2 per batch
    low = shuffled_data[shuffled_data['Category'] == '<25']    # 1 per batch
    
    high_idx, mid_idx, low_idx = 0, 0, 0
    
    while high_idx < len(high) or mid_idx < len(mid) or low_idx < len(low):
        batch_students = []
        
        if high_idx < len(high):
            batch_students.append(high.iloc[high_idx])
            high_idx += 1
        
        if mid_idx < len(mid):
            batch_students.append(mid.iloc[mid_idx])
            mid_idx += 1
            if mid_idx < len(mid) and len(batch_students) < 5:
                batch_students.append(mid.iloc[mid_idx])
                mid_idx += 1
        
        if low_idx < len(low) and len(batch_students) < 5:
            batch_students.append(low.iloc[low_idx])
            low_idx += 1
        
        if batch_students:
            batch_df = pd.concat([student.to_frame().T for student in batch_students], ignore_index=True)
            grouped_batches.append(batch_df)
    
    return grouped_batches

def assign_weekly_topics(groups, topics_list, weeks=5):
    time.sleep(1)  # Kept at 1 second for topic assignment
    topic_cycle = itertools.cycle(topics_list)
    assigned_weeks = []
    
    for week in range(1, weeks + 1):
        assigned_topics = []
        used_topics = set()
        
        for group_idx, group in enumerate(groups):
            topic = next(topic_cycle)
            while topic['Topic'] in used_topics:
                topic = next(topic_cycle)
            used_topics.add(topic['Topic'])
            assigned_topics.append({"Week": week, "Batch": f"Batch {group_idx + 1}", "Topic": topic["Topic"]})
        
        assigned_weeks.append(assigned_topics)
    
    return assigned_weeks

def create_structured_output(batches, weekly_assignments):
    time.sleep(1)  # Reduced to 1 second
    result_data = []
    
    for batch_idx, batch in enumerate(batches):
        batch_name = f"Batch {batch_idx + 1}"
        for _, student in batch.iterrows():
            result_data.append({"Name": student["Name"], "Batch": batch_name})
    
    result_df = pd.DataFrame(result_data)
    
    for week_assignments in weekly_assignments:
        week_num = week_assignments[0]["Week"]
        week_topics = {assignment["Batch"]: assignment["Topic"] for assignment in week_assignments}
        result_df[f"Week {week_num} Topic"] = result_df["Batch"].map(week_topics)
    
    return result_df

st.title("Student Clustering & Weekly Topic Assignment")

uploaded_file = st.file_uploader("Upload CSV (Columns: Name, Marks)", type=["csv"])

if uploaded_file:
    with st.spinner("Loading data..."):
        data = load_data(uploaded_file)
    
    if data is not None:
        st.success("Data Loaded Successfully!")
        st.write("### Student Marks Data")
        st.write(data)

        with st.spinner("Categorizing students..."):
            data = categorize_students(data)
        st.success("Categorization Completed!")
        st.write("### Categorized Students")
        st.write(data)

        with st.spinner("Creating custom batches..."):
            grouped_batches = create_custom_batches(data)
        st.success("Batches Created Successfully!")
        st.write("### Batches (Custom Rules: >35: 1, 25-35: 2, <25: 1)")
        for i, batch in enumerate(grouped_batches):
            st.write(f"Batch {i + 1}:")
            st.write(batch)

        with st.spinner("Assigning weekly topics..."):
            weekly_assignments = assign_weekly_topics(grouped_batches, topics_data, weeks=5)
        st.success("Topics Assigned Successfully!")

        with st.spinner("Generating structured output..."):
            structured_output = create_structured_output(grouped_batches, weekly_assignments)
        st.success("Structured Output Generated!")
        st.write("### Structured Output: Name, Batch, Weekly Topics")
        st.write(structured_output)
        
        csv_file = structured_output.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Structured Output",
            data=csv_file,
            file_name="student_batch_topics.csv",
            mime='text/csv'
        )

        if st.button("Regenerate Data"):
            st.experimental_rerun()