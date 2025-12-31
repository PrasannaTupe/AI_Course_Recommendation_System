from flask import Flask, render_template, request
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# Load precomputed data
jobs_df = pd.read_pickle("jobs.pkl")
udemy_df = pd.read_pickle("udemy_with_emb.pkl")
coursera_df = pd.read_pickle("coursera_with_emb.pkl")
job_embeddings = torch.load("job_embeddings.pt")
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# After loading DataFrames:
def ensure_course_emb_cpu(df):
    df["course_emb"] = df["course_emb"].apply(lambda emb: emb.cpu() if emb is not None and hasattr(emb, 'cpu') else None)
    return df

udemy_df = ensure_course_emb_cpu(udemy_df)
coursera_df = ensure_course_emb_cpu(coursera_df)

job_embeddings = job_embeddings.cpu()

def match_role(user_role):
    user_emb = model.encode(user_role, convert_to_tensor=True).cpu()
    sim_scores = util.cos_sim(user_emb, job_embeddings)[0]
    best_idx = sim_scores.argmax().item()
    return jobs_df.iloc[best_idx]["Job Title"]

# Skill gap function (update as per your fixed version)
def skill_gap(user_skills_dict, job_title):
    import ast
    job_skills_str = jobs_df.loc[jobs_df["Job Title"] == job_title, "Cleaned_Job_Skills"].values[0]
    try:
        job_skills = ast.literal_eval(job_skills_str)
        job_skills = [s.lower().strip() for s in job_skills]
    except:
        job_skills = []
    user_skills = {k.lower().strip(): v for k, v in user_skills_dict.items()}
    strong, weak, missing = [], [], []
    for skill, rating in user_skills.items():
        if skill in job_skills:
            if rating >= 3:
                strong.append(skill)
            else:
                weak.append(skill)
    for skill in job_skills:
        if skill not in user_skills:
            missing.append(skill)
    return strong, weak, missing

# Course recommendation function
def recommend_courses_fast(dataframe, missing_skills, weak_skills, top_n=100):
    target_skills = list(set(missing_skills + weak_skills))
    if not target_skills:
        return []
    target_embeddings = model.encode(target_skills, convert_to_tensor=True).cpu()
    target_emb = torch.mean(target_embeddings, dim=0, keepdim=True)
    course_scores = []
    for _, row in dataframe.iterrows():
        course_emb = row.get("course_emb")
        if course_emb is None:
            continue
        course_emb = course_emb.cpu()  # <----- add this for safety!
        sim = util.cos_sim(target_emb, course_emb).item()
        if sim >= 0.5:
            title = row.get("Title", "")
            link = row.get("Link", "")
            enrollment = int(row.get("Enrollment", 0))
            rating = float(row.get("Stars", 0))
            course_scores.append({
                "title": title,
                "link": link,
                "enrollment": enrollment,
                "rating": rating,
                "score": round(sim, 2)
            })
    course_scores = sorted(course_scores, key=lambda x: x["score"], reverse=True)
    return course_scores[:top_n]

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations_udemy = []
    recommendations_coursera = []
    matched_role = ""
    strong, weak, missing = [], [], []

    if request.method == "POST":
        user_role = request.form.get("role", "")
        raw_skills = request.form.getlist("skill[]")
        raw_ratings = request.form.getlist("rating[]")

        # Build dict of skill:rating
        try:
            user_skills = {str(s).lower().strip(): int(r) for s, r in zip(raw_skills, raw_ratings) if s.strip()}
        except:
            user_skills = {}

        if user_role.strip() and user_skills:
            matched_role = match_role(user_role)
            strong, weak, missing = skill_gap(user_skills, matched_role)
            recommendations_udemy = recommend_courses_fast(udemy_df, missing, weak, top_n=20)
            recommendations_coursera = recommend_courses_fast(coursera_df, missing, weak, top_n=20)

    return render_template("index.html",
                           role=matched_role,
                           strong=strong,
                           weak=weak,
                           missing=missing,
                           udemy=recommendations_udemy,
                           coursera=recommendations_coursera)

if __name__ == "__main__":
    app.run(debug=True)
