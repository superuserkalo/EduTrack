import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Constants
DEFAULT_TOPIC = "Topic 1"
DEFAULT_RATING = "-"
MAX_STUDENT_NAME_LENGTH = 128

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables if they don't exist."""
    if 'students' not in st.session_state:
        st.session_state.students = []  # List to store student data
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""  # Temporary storage for input student name
    if 'topics' not in st.session_state:
        st.session_state.topics = [DEFAULT_TOPIC]  # List of topics, starts with one default topic
    if 'ratings' not in st.session_state:
        st.session_state.ratings = [DEFAULT_RATING]  # List of ratings, corresponds to topics
    if 'edit_modes' not in st.session_state:
        st.session_state.edit_modes = [False]  # List of booleans to track edit mode for each topic
    if 'delete_topic_index' not in st.session_state:
        st.session_state.delete_topic_index = None  # Stores index of topic to be deleted
    if 'pending_delete_topic' not in st.session_state:
        st.session_state.pending_delete_topic = None

initialize_session_state()

def toggle_edit_mode(index):
    """
    Toggle the edit mode for a specific topic.
    
    Args:
        index (int): The index of the topic to toggle.
    
    This function switches a topic between view and edit mode.
    When entering edit mode, it initializes the edit value with the current topic name.
    """
    st.session_state.edit_modes[index] = not st.session_state.edit_modes[index]
    if st.session_state.edit_modes[index]:
        st.session_state[f"edit_{index}"] = st.session_state.topics[index]

def confirm_topic_edit(index):
    """
    Confirm the edit for a specific topic.
    
    Args:
        index (int): The index of the topic to confirm edit.
    
    This function updates the topic name with the edited value and exits edit mode.
    """
    st.session_state.topics[index] = st.session_state[f"edit_{index}"]
    st.session_state.edit_modes[index] = False

def map_rating(rating):
    """
    Map rating symbols to numerical values.
    
    Args:
        rating (str): The rating symbol ('+', '~', or '-').
    
    Returns:
        int: The numerical value of the rating.
    
    This function converts symbolic ratings to numerical values for data processing.
    """
    rating_map = {'+': 10, '~': 5, '-': 0}
    return rating_map.get(rating, 0)

def add_new_topic():
    """
    Add a new topic to the session state.
    
    This function creates a new topic with a default name and rating,
    and initializes its edit mode to False.
    """
    new_topic = f"Topic {len(st.session_state.topics) + 1}"
    st.session_state.topics.append(new_topic)
    st.session_state.ratings.append(DEFAULT_RATING)
    st.session_state.edit_modes.append(False)

def delete_topic(index):
    """
    Mark a topic for potential deletion.
    
    Args:
        index (int): The index of the topic to potentially delete.
    """
    st.session_state.pending_delete_topic = index

def cancel_delete_topic():
    """Cancel the pending topic deletion."""
    st.session_state.pending_delete_topic = None

def confirm_delete_topic(index):
    """
    Confirm the deletion of a topic.
    
    Args:
        index (int): The index of the topic to delete.
    """
    st.session_state.delete_topic_index = index
    st.session_state.pending_delete_topic = None

def process_topic_deletion():
    """Process the deletion of a marked topic."""
    if st.session_state.delete_topic_index is not None:
        if len(st.session_state.topics) > 1:
            index = st.session_state.delete_topic_index
            deleted_topic = st.session_state.topics[index]
            
            # Remove the topic from the main lists
            del st.session_state.topics[index]
            del st.session_state.ratings[index]
            del st.session_state.edit_modes[index]
            
            # Remove the topic from all students' data
            for student in st.session_state.students:
                if deleted_topic in student['Topics']:
                    topic_index = student['Topics'].index(deleted_topic)
                    del student['Topics'][topic_index]
                    del student['Ratings'][topic_index]
            
            st.success(f"Topic '{deleted_topic}' has been removed.")
        else:
            st.error("Cannot delete the last remaining topic.")
        st.session_state.delete_topic_index = None
        st.session_state.pending_delete_topic = None  # Reset pending deletion

def render_topic_interface():
    """Render the interface for managing topics and ratings."""
    for i, topic in enumerate(st.session_state.topics):
        col1, col2, col3, col4, col5 = st.columns([4, 2, 0.5, 0.5, 0.5])

        with col1:
            if st.session_state.edit_modes[i]:
                new_topic = st.text_input(f"Edit Topic {i+1}", value=st.session_state[f"edit_{i}"], key=f"edit_{i}")
            else:
                st.write(topic)

        with col2:
            st.write(f"Rating for {topic}:")
            st.session_state.ratings[i] = st.selectbox("", options=['-', '~', '+'], key=f"rating_{i}", 
                index=0 if st.session_state.ratings[i] == '-' else (1 if st.session_state.ratings[i] == '~' else 2),
                label_visibility="collapsed")

        with col3:
            st.write("")  # Spacer column

        with col4:
            if st.session_state.pending_delete_topic == i:
                st.button("✅", on_click=confirm_delete_topic, args=(i,), key=f"confirm_delete_{i}")
            elif st.session_state.edit_modes[i]:
                st.button("✅", on_click=confirm_topic_edit, args=(i,), key=f"confirm_edit_{i}")
            else:
                st.button("✏️", on_click=toggle_edit_mode, args=(i,), key=f"edit_button_{i}")

        with col5:
            if st.session_state.pending_delete_topic == i:
                st.button("❌", on_click=cancel_delete_topic, key=f"cancel_delete_{i}")
            else:
                st.button("🗑️", on_click=delete_topic, args=(i,), key=f"delete_button_{i}")

def validate_student_name(name):
    """Validate the student name input."""
    if not name:
        return "Student name cannot be empty. Please enter a name."
    if len(name) > MAX_STUDENT_NAME_LENGTH:
        return f"Student name cannot exceed {MAX_STUDENT_NAME_LENGTH} characters. Please enter a shorter name."
    if name != name.strip():
        return "Student name cannot have leading or trailing whitespaces. Please enter a valid name."
    if any(student['Name'] == name for student in st.session_state.students):
        return f"Student {name} already exists. Please enter a different name."
    return None

def add_student():
    """
    Handle the addition of a new student and manage topic interface.
    
    This function is the core of the application's UI. It manages:
    1. The input field for student names
    2. The display and editing of topics
    3. The rating selection for each topic
    4. The addition of new topics
    5. The deletion of existing topics
    6. The validation and addition of new students to the database
    """
    st.write("Student Name:")
    col1, col2, col3 = st.columns([3, 1, 2])
    
    with col1:
        student_name = st.text_input("", value=st.session_state.student_name, label_visibility="collapsed", max_chars=32)
    
    with col2:
        st.write("")  # Spacer column
    
    with col3:
        confirm_button = st.button("Add Student", use_container_width=True)

    process_topic_deletion()
    render_topic_interface()

    # Add New Topic button
    if st.button("+ Add New Topic", type="secondary", key="add_new_topic"):
        add_new_topic()
        st.rerun()

    # Process student addition
    if confirm_button:
        error_message = validate_student_name(student_name)
        if error_message:
            st.error(error_message)
        else:
            numerical_ratings = [map_rating(r) for r in st.session_state.ratings]
            st.session_state.students.append({
                "Name": student_name,
                "Topics": st.session_state.topics.copy(),
                "Ratings": numerical_ratings
            })
            st.success(f"Student {student_name} added successfully!")
            st.session_state.student_name = ""
            st.session_state.ratings = [DEFAULT_RATING] * len(st.session_state.topics)

def generate_class_performance_chart():
    """
    Generate and display the class-wide performance chart.
    
    This function creates a bar chart showing the number of '+' ratings
    for each current topic across all students.
    """
    if not st.session_state.students:
        st.warning("No students added yet.")
        return

    topic_counts = {topic: 0 for topic in st.session_state.topics}
    
    for student in st.session_state.students:
        for topic, rating in zip(student['Topics'], student['Ratings']):
            if topic in topic_counts and rating == 10:  # 10 corresponds to '+'
                topic_counts[topic] += 1
    
    df = pd.DataFrame({
        "Topic": list(topic_counts.keys()),
        "Number of '+' Ratings": list(topic_counts.values())
    })
    
    df = df.sort_values("Number of '+' Ratings", ascending=False)
    
    fig = px.bar(df, x="Topic", y="Number of '+' Ratings", 
                 title="Class Performance by Topic (Number of '+' Ratings)")
    
    st.plotly_chart(fig)

def generate_individual_performance_chart(student):
    """
    Generate and display an individual student's performance chart.
    
    Args:
        student (dict): The student's data containing 'Topics' and 'Ratings'.
    
    This function creates a radar chart showing the student's performance
    across all topics.
    """
    # Filter out topics and ratings that are no longer in the current topic list
    current_topics = st.session_state.topics
    topics = [topic for topic in student['Topics'] if topic in current_topics]
    ratings = [rating for topic, rating in zip(student['Topics'], student['Ratings']) if topic in current_topics]

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

def reset_data():
    """
    Reset all student data and ratings.
    
    This function clears all stored student data and resets ratings,
    effectively resetting the application to its initial state.
    """
    st.session_state.students = []
    st.session_state.student_name = ""
    st.session_state.ratings = [DEFAULT_RATING] * len(st.session_state.topics)
    st.success("All data has been reset.")

def main():
    """Main function to run the Streamlit app."""
    st.title("Edutrack")

    add_student()

    if st.sidebar.button("Reset Data"):
        reset_data()

    # Display performance charts
    tabs = st.tabs(["Class Performance"] + [student['Name'] for student in st.session_state.students])

    with tabs[0]:
        st.header("Class Performance")
        generate_class_performance_chart()

    for i, student in enumerate(st.session_state.students):
        with tabs[i + 1]:
            st.header(f"Performance for {student['Name']}")
            generate_individual_performance_chart(student)

if __name__ == "__main__":
    main()
