from dotenv import load_dotenv
import os
import streamlit as st
from prompt_templates.prompts import (
    role, plus_minus, keys, recommendations,
    optimization, bullet_opt, key_opt, output, summary
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate, LLMChain
from langchain.chains import SequentialChain
import google.generativeai as genai

load_dotenv()

# Initialize the Gemini API and LLM
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = 'gemini-1.5-flash'
model = ChatGoogleGenerativeAI(model=model_name)

# Prompt Templates
strengths_weaknesses_template = PromptTemplate(
    input_variables=["description", "resume"],
    template=f"{role}\n\n{plus_minus}\n\nJob Description:\n\n{{description}}\n\nResume:\n\n{{resume}}"
)

missing_keywords_template = PromptTemplate(
    input_variables=["description", "resume"],
    template=f"{role}\n\n{keys}\n\nJob Description:\n\n{{description}}\n\nResume:\n\n{{resume}}"
)

recommendations_template = PromptTemplate(
    input_variables=["strengths_weaknesses", "missing_keywords"],
    template=f"{recommendations}\n\nStrengths and Weaknesses:\n\n{{strengths_weaknesses}}\n\nMissing Keywords:\n\n{{missing_keywords}}"
)

bullet_opt_template = PromptTemplate(
    input_variables=["resume", "description", "evaluation"],
    template=f"{optimization}\n\n{bullet_opt}\n\nResume:\n{{resume}}\n\nJob Description:\n\n{{description}}\n\nEvaluation Report:\n{{evaluation}}"
)

key_opt_template = PromptTemplate(
    input_variables=["resume", "description", "evaluation"],
    template=f"{optimization}\n\n{key_opt}\n\nResume:\n{{resume}}\n\nJob Description:\n\n{{description}}\n\nEvaluation Report:\n{{evaluation}}"
)

output_template = PromptTemplate(
    input_variables=["resume"],
    template=f"{output}\n\nOptimized Resume:\n\n{{resume}}"
)

summary_template = PromptTemplate(
    input_variables=["original_resume", "optimized_resume"],
    template=f"{summary}\n\nOriginal Resume:\n\n{{original_resume}}\n\nOptimized Resume:\n\n{{optimized_resume}}"
)

# Chains
strengths_weaknesses_chain = LLMChain(llm=model, prompt=strengths_weaknesses_template, output_key="strengths_weaknesses")
missing_keywords_chain = LLMChain(llm=model, prompt=missing_keywords_template, output_key="missing_keywords")
recommendations_chain = LLMChain(llm=model, prompt=recommendations_template, output_key="recommendations")

bullet_opt_chain = LLMChain(llm=model, prompt=bullet_opt_template, output_key="bullet_optimized")
key_opt_chain = LLMChain(llm=model, prompt=key_opt_template, output_key="keyword_optimized")
output_chain = LLMChain(llm=model, prompt=output_template, output_key="formatted_resume")
summary_chain = LLMChain(llm=model, prompt=summary_template, output_key="summary")

optimization_chain = SequentialChain(
    chains=[bullet_opt_chain, key_opt_chain, output_chain],
    input_variables=["resume", "description", "evaluation"],
    output_variables=["bullet_optimized", "keyword_optimized", "formatted_resume"],
)

# Streamlit App
st.set_page_config(page_title="AI-Powered Resume Alignment Engine", layout="wide")
st.header("AI-Powered Resume Alignment Engine")

col1, col2 = st.columns(2)
with col1:
    description = st.text_area("Job Description:", height=300, key="desc")
with col2:
    resume = st.text_area("Resume:", height=300, key="resume")

evaluate_col, optimize_col = st.columns(2)
evaluate = evaluate_col.button("Evaluate My Resume")
optimize = optimize_col.button("Optimize My Resume")

def run_evaluation(description, resume):
    strengths_weaknesses = strengths_weaknesses_chain.run({"description": description, "resume": resume})
    missing_keywords = missing_keywords_chain.run({"description": description, "resume": resume})
    recommendations_response = recommendations_chain.run({
        "strengths_weaknesses": strengths_weaknesses,
        "missing_keywords": missing_keywords
    })
    return strengths_weaknesses, missing_keywords, recommendations_response

if evaluate:
    if description and resume:
        with st.spinner("Analyzing resume..."):
            strengths_weaknesses, missing_keywords, recommendations_response = run_evaluation(description, resume)
            st.subheader("Strengths and Weaknesses")
            st.write(strengths_weaknesses)
            st.subheader("Missing Keywords")
            st.write(missing_keywords)
            st.subheader("Actionable Recommendations")
            st.write(recommendations_response)
    else:
        st.warning("Please provide both resume and job description.")

if optimize:
    if description and resume:
        with st.spinner("Optimizing resume..."):
            strengths_weaknesses, missing_keywords, recommendations_response = run_evaluation(description, resume)
            evaluation = f"Strengths and Weaknesses:\n{strengths_weaknesses}\n\nMissing Keywords:\n{missing_keywords}\n\nRecommendations:\n{recommendations_response}"
            
            optimization_result = optimization_chain(
                {"resume": resume, "description": description, "evaluation": evaluation}
            )
            
            optimized_resume = optimization_result["formatted_resume"]
            
            summary_result = summary_chain.run({
                "original_resume": resume,
                "optimized_resume": optimized_resume
            })
            
            st.subheader("Optimized Resume")
            st.write(optimized_resume)
            st.subheader("Summary of Changes")
            st.write(summary_result)
    else:
        st.warning("Please provide both resume and job description.")
