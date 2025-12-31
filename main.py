import streamlit as st

# Dummy course recommendations based on skills
COURSES = {
    "Python": ["Python for Beginners", "Advanced Python Programming"],
    "Machine Learning": ["Intro to Machine Learning", "Deep Learning Specialization"],
    "Data Visualization": ["Data Visualization with Python", "Advanced Tableau"],
    "SQL": ["SQL for Data Analysis", "Advanced SQL Queries"],
    "Statistics": ["Statistics for Data Science", "Advanced Statistical Methods"],
    "HTML": ["Learn HTML from Scratch", "Responsive Web Design with HTML"],
    "CSS": ["Master CSS", "Advanced CSS Techniques"],
    "JavaScript": ["JavaScript for Beginners", "Advanced JavaScript"],
    "React": ["React Basics", "Master React in 3 Weeks"],
    "Node.js": ["Node.js for Beginners", "Building APIs with Node.js"]
}

def main():
    st.title("Course Recommendation System")
    st.write("Welcome to the Course Recommendation System!")

    # User enters their main goal
    goal = st.text_input("Enter your main goal (e.g., 'Become a Data Scientist'):")

    if goal:
        st.write(f"Your main goal is: {goal}")

        # Collect skills from the user
        skills = {}
        add_more_skills = True

        while add_more_skills:
            skill = st.text_input("Enter a skill you need (e.g., 'Python'):")
            if skill:
                # Rating for the skill
                rating = st.slider(f"Rate your {skill} skill from 0 (No Knowledge) to 5 (Expert):", 0, 5, 3)
                skills[skill] = rating
            # Ask if the user wants to add another skill
            add_more_skills = st.checkbox("Add another skill?", value=False)

        # If no skills are added, ask the user to provide some
        if not skills:
            st.warning("Please add at least one skill to proceed.")
            return

        st.write("Your entered skills and ratings:")
        for skill, rating in skills.items():
            st.write(f"- {skill}: {rating}")

        # Define the missing skills
        st.write("\nCalculating missing skills...")

        # Let's assume an arbitrary threshold of rating (e.g., 3) to decide missing skills.
        missing_skills = {skill: 3 - rating for skill, rating in skills.items() if rating < 3}

        if missing_skills:
            st.write("You are missing the following skills:")
            for skill, deficit in missing_skills.items():
                st.write(f"- {skill} (Need to improve by {deficit} points)")

            # Recommend courses based on missing skills
            st.write("\nBased on your missing skills, here are some course recommendations:")
            for skill in missing_skills:
                st.write(f"### {skill}:")
                for course in COURSES.get(skill, []):
                    st.write(f"- {course}")
        else:
            st.write("You have all the necessary skills for your goal!")

if __name__ == "__main__":
    main()

