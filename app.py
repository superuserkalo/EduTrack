import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialize session state for students data, student name, and ratings
if 'students' not in st.session_state:
    st.session_state.students = []
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""
if 'ratings' not in st.session_state:
    st.session_state.ratings = ["-", "-", "-", "-", "-"]
if 'topics' not in st.session_state:
    st.session_state.topics = ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]
if 'edit_modes' not in st.session_state:
    st.session_state.edit_modes = [False] * len(st.session_state.topics)

# Function to toggle the edit mode of a topic
def toggle_edit_mode(index):
    st.session_state.edit_modes[index] = not st.session_state.edit_modes[index]

# Function to map ratings to numerical values
def map_rating(rating):
    if rating == '+':
        return 10
    elif rating == '~':
        return 5
    elif rating == '-':
        return 0
    else:
        return 0

# Function to add a new student
def add_student():
    student_name = st.text_input("Student Name:", value=st.session_state.student_name)
    ratings = []

    # Loop over topics and create the rating interface with pencil edit button
    for i, topic in enumerate(st.session_state.topics):
        col1, col2, col3 = st.columns([4, 2, 1])  # Create three columns for topic, rating, and pencil button

        with col1:
            if st.session_state.edit_modes[i]:
                # If in edit mode, allow inline editing of the topic
                new_topic = st.text_input(f"Edit Topic {i+1}", value=topic, key=f"edit_{i}")
                st.session_state.topics[i] = new_topic  # Update the topic
            else:
                # Display topic as text when not in edit mode
                st.write(topic)

        with col2:
            # Select rating for each topic
            st.session_state.ratings[i] = st.selectbox(f"Rating for {topic}:", options=['-', '~', '+'], key=f"rating_{i}", index=0 if st.session_state.ratings[i] == '-' else (1 if st.session_state.ratings[i] == '~' else 2))
            ratings.append(st.session_state.ratings[i])

        with col3:
            # Show a pencil icon to switch to edit mode
            st.button("✏️", on_click=toggle_edit_mode, args=(i,), key=f"edit_button_{i}")

    if st.button("Confirm Add Student"):
        # Check if student name is empty
        if not student_name:
            st.error("Student name cannot be empty. Please enter a name.")
        # Check if student name exceeds 128 characters
        elif len(student_name) > 128:
            st.error("Student name cannot exceed 128 characters. Please enter a shorter name.")
        # Check if student name has leading or trailing whitespaces
        elif student_name != student_name.strip():
            st.error("Student name cannot have leading or trailing whitespaces. Please enter a valid name.")
        # Check if student already exists
        elif any(student['Name'] == student_name for student in st.session_state.students):
            st.error(f"Student {student_name} already exists. Please enter a different name.")
        else:
            numerical_ratings = [map_rating(r) for r in ratings]
            st.session_state.students.append({
                "Name": student_name,
                "Topics": st.session_state.topics,
                "Ratings": numerical_ratings
            })
            st.success(f"Student {student_name} added successfully!")
            # Clear the student name and ratings fields
            st.session_state.student_name = ""
            st.session_state.ratings = ["-"] * len(st.session_state.topics)

# Function to generate class-wide performance chart
def generate_class_performance_chart():
    if not st.session_state.students:
        st.warning("No students added yet.")
        return

    all_ratings = [student['Ratings'] for student in st.session_state.students]
    avg_ratings = [sum(col) / len(col) for col in zip(*all_ratings)]

    df = pd.DataFrame({
        "Topic": st.session_state.students[0]['Topics'],
        "Average Rating": avg_ratings
    })

    fig = px.bar(df, x="Topic", y="Average Rating", title="Class Performance by Topic")
    st.plotly_chart(fig)

# Function to generate individual student performance chart
def generate_individual_performance_chart(student):
    topics = student['Topics']
    ratings = student['Ratings']

    fig = go.Figure(data=go.Scatterpolar(
        r=ratings,
        theta=topics,
        fill='toself',
        name=student['Name']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title=f"Performance Chart for {student['Name']}"
    )

    st.plotly_chart(fig)

# Function to reset all data
def reset_data():
    st.session_state.students = []
    st.session_state.student_name = ""
    st.session_state.ratings = ["-"] * len(st.session_state.topics)
    st.success("All data has been reset.")

# Streamlit App Layout
st.title("Math Analytics App")

# Add student data entry form
add_student()

if st.sidebar.button("Reset Data"):
    reset_data()

# Main area for displaying charts
tabs = st.tabs(["Class Performance"] + [student['Name'] for student in st.session_state.students])

with tabs[0]:
    st.header("Class Performance")
    generate_class_performance_chart()

for i, student in enumerate(st.session_state.students):
    with tabs[i + 1]:
        st.header(f"Performance for {student['Name']}")
        generate_individual_performance_chart(student)