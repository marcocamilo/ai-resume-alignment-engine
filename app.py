import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain.chains import SequentialChain
from langchain_google_genai import ChatGoogleGenerativeAI

from src.prompt_templates.prompts import (
    bullet_opt,
    key_opt,
    keys,
    minus,
    optimization,
    output,
    plus,
    recommendations,
    role,
    summary,
)

load_dotenv()

#  ────────────────────────────────────────────────────────────────────
#   INITIALIZE THE GEMINI API AND LLM
#  ────────────────────────────────────────────────────────────────────
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "gemini-1.5-flash"
model = ChatGoogleGenerativeAI(model=model_name)

#  ────────────────────────────────────────────────────────────────────
#   EVALUATION CHAINS
#  ────────────────────────────────────────────────────────────────────
strengths_template = PromptTemplate(
    input_variables=["description", "resume"],
    template=f"{role}\n\n{plus}\n\nJob Description:\n\n{{description}}\n\nResume:\n\n{{resume}}",
)

weaknesses_template = PromptTemplate(
    input_variables=["description", "resume"],
    template=f"{role}\n\n{minus}\n\nJob Description:\n\n{{description}}\n\nResume:\n\n{{resume}}",
)

missing_keywords_template = PromptTemplate(
    input_variables=["description", "resume"],
    template=f"{role}\n\n{keys}\n\nJob Description:\n\n{{description}}\n\nResume:\n\n{{resume}}",
)

evaluation_template = PromptTemplate(
    input_variables=["strengths", "weaknesses", "missing_keywords"],
    template=f"{recommendations}\n\nStrengths and Weaknesses:\n\n{{strengths}}\n\n{{weaknesses}}\n\nMissing Keywords:\n\n{{missing_keywords}}",
)

evaluation_chains = {
    "strengths": LLMChain(llm=model, prompt=strengths_template, output_key="strengths"),
    "weaknesses": LLMChain(
        llm=model, prompt=weaknesses_template, output_key="weaknesses"
    ),
    "missing_keywords": LLMChain(
        llm=model, prompt=missing_keywords_template, output_key="missing_keywords"
    ),
    "recommendations": LLMChain(
        llm=model, prompt=evaluation_template, output_key="recommendations"
    ),
}

#  ────────────────────────────────────────────────────────────────────
#   OPTIMIZATION TEMPLATES
#  ────────────────────────────────────────────────────────────────────
bullet_opt_template = PromptTemplate(
    input_variables=["resume", "description", "evaluation"],
    template=f"{optimization}\n\n{bullet_opt}\n\nResume:\n{{resume}}\n\nJob Description:\n\n{{description}}\n\nEvaluation Report:\n{{evaluation}}",
)

key_opt_template = PromptTemplate(
    input_variables=["bullet_optimized", "description", "evaluation"],
    template=f"{optimization}\n\n{key_opt}\n\nResume:\n{{bullet_optimized}}\n\nJob Description:\n\n{{description}}\n\nEvaluation Report:\n{{evaluation}}",
)

output_template = PromptTemplate(
    input_variables=["keyword_optimized"],
    template=f"{output}\n\nOptimized Resume:\n\n{{keyword_optimized}}",
)

summary_template = PromptTemplate(
    input_variables=["resume", "optimized_resume"],
    template=f"{summary}\n\nOriginal Resume:\n\n{{resume}}\n\nOptimized Resume:\n\n{{optimized_resume}}",
)

optimization_chains = {
    "bullet_opt": LLMChain(
        llm=model, prompt=bullet_opt_template, output_key="bullet_optimized"
    ),
    "key_opt": LLMChain(
        llm=model, prompt=key_opt_template, output_key="keyword_optimized"
    ),
    "output": LLMChain(llm=model, prompt=output_template, output_key="final_resume"),
    "summary": LLMChain(llm=model, prompt=summary_template, output_key="summary"),
}

#  ────────────────────────────────────────────────────────────────────
#   SEQUENTIAL CHAIN
#  ────────────────────────────────────────────────────────────────────
evaluation_chain = SequentialChain(
    chains=[
        evaluation_chains["strengths"],
        evaluation_chains["weaknesses"],
        evaluation_chains["missing_keywords"],
        evaluation_chains["recommendations"],
    ],
    input_variables=["resume", "description"],
    output_variables=["strengths", "weaknesses", "missing_keywords", "recommendations"],
)

optimization_chain = SequentialChain(
    chains=[
        optimization_chains["bullet_opt"],
        optimization_chains["key_opt"],
        optimization_chains["output"],
    ],
    input_variables=["resume", "description", "evaluation"],
    output_variables=["final_resume"],
)

#  ────────────────────────────────────────────────────────────────────
#   STREAMLIT APP
#  ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI-Powered Resume Alignment Engine", layout="wide")
st.header("AI-Powered Resume Alignment Engine")

col1, col2 = st.columns(2)
with col1:
    description = st.text_area("Job Description:", height=200, key="desc")
    evaluate = st.button("Evaluate My Resume")
with col2:
    resume = st.text_area("Resume:", height=200, key="resume")
    optimize = st.button("Optimize My Resume")

if evaluate:
    if description and resume:
        with st.spinner("Analyzing resume..."):
            strengths, weaknesses, missing_keywords, evaluation_response = (
                evaluation_chain(
                    {"description": description, "resume": resume},
                    return_only_outputs=True,
                ).values()
            )
            st.subheader("Strengths and Weaknesses")
            col_s, col_w = st.columns(2)
            with col_s:
                st.write(strengths)
            with col_w:
                st.write(weaknesses)
            st.subheader("Missing Keywords")
            st.write(missing_keywords)
            st.subheader("Actionable Recommendations")
            st.write(evaluation_response)
    else:
        st.warning("Please provide both resume and job description.")

if optimize:
    if description and resume:
        with st.spinner("Optimizing resume..."):
            strengths, weaknesses, missing_keywords, evaluation_response = (
                evaluation_chain(
                    {"description": description, "resume": resume},
                    return_only_outputs=True,
                ).values()
            )
            evaluation = f"Strengths and Weaknesses:\n{strengths}\n\n{weaknesses}\n\nMissing Keywords:\n{missing_keywords}\n\nRecommendations:\n{evaluation_response}"

            optimization_result = optimization_chain(
                {"resume": resume, "description": description, "evaluation": evaluation}
            )

            optimized_resume = optimization_result["final_resume"]

            summary_result = optimization_chains["summary"].run(
                {"resume": resume, "optimized_resume": optimized_resume}
            )

            st.subheader("Optimized Resume")
            st.text(optimized_resume)
            st.subheader("Summary of Changes")
            st.write(summary_result)
    else:
        st.warning("Please provide both resume and job description.")
