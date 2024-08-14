from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt, description, resume):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([description, resume, prompt])
    return response.text

## Streamlit App

st.set_page_config(page_title="AI-Powered Resume Alignment Engine")
st.header("AI-Powered Resume Alignment Engine")
description=st.text_area("Job Description: ",key="desc")
resume=st.text_area("Resume: ",key="resume")

evaluate = st.button("Evaluate My Resume")

role = "You are an experienced Human Resources Manager, specializing in analyzing resumes and providing recommendations that help job seekers optimize their resumes. Your task is to evaluate the alignment between the provided resume and job description and provide an expert's evaluation on whether the candidate had the best profile for the role.You are an experienced Human Resources Manager, specializing in analyzing resumes and providing recommendations that help job seekers optimize their resumes. Your task is to evaluate the alignment between the provided resume and job description and provide an expert's evaluation on whether the candidate had the best profile for the role. Focus only on the following task:"

plus_minus = """1. List of Strengths and Weaknesses 

Create a list of the resume's strengths and weaknesses linked to the job description. Under each strength, give a concrete example or observation found in resume demonstrating the strength/weakness. Under each weakness, give a concrete example of how an enhancement would look like.

For each one, provide the following format: 

**Strengths**
- '[strength]: one-sentence brief explanation.' 
    - Example: concrete example
**Weakness**
- '[weakness]: one-sentence brief explanation.' 
    - Example: concrete example

Do not include a header for this task"""

keys = """2. Missing Keywords

List the keywords from the job description that are missing in the resume, specially skills, tools/frameworks, and behavioral adjectives. Provide only the keywords and phrases, without explanations. Make sure to breakdown list of keywords into separate bullet points.

Do not include a header for this task"""

recommendations = """3. Actionable Recommendations

Provide a series of actionable recommendations to enhance elements of the resume. Based your recommendations exclusively on the strengths, weaknesses, and missing keywords you identified in the previous tasks. Include suggestions for modifying bullet points, adding relevant skills, and incorporating missing keywords. Ensure the recommendations are specific, practical, and aimed at making the resume as competitive as possible. 

Provide each recommendation in the following format: 

- '[actionable recommendation]: brief explanation.' 
    - Concrete example(s)

Do not include a header for this task"""

strengths_weaknesses_prompt = '\n\n'.join([role, plus_minus])
missing_keywords_prompt = '\n\n'.join([role, keys])
recommendations_prompt = '\n\n'.join([role, recommendations])

if evaluate:
    if description and resume:
        strengths_weaknesses = get_gemini_response(strengths_weaknesses_prompt, description, resume)
        st.subheader("Strengths and Weaknesses")
        st.write(strengths_weaknesses)

        missing_keywords = get_gemini_response(missing_keywords_prompt, description, resume)
        st.subheader("Missing Keywords")
        st.write(missing_keywords)

        full_recommendations_prompt = f"{recommendations_prompt}\n\nStrengths and Weaknesses:\n{strengths_weaknesses}\n\nMissing Keywords:\n{missing_keywords}"
        recommendations_response = get_gemini_response(full_recommendations_prompt, description, resume)
        st.subheader("Actionable Recommendations")
        st.write(recommendations_response)
    else:
        st.write("Please provide both resume and job description.")
