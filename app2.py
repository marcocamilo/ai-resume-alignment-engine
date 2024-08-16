import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import PromptTemplate
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
llm = ChatGoogleGenerativeAI(model=model_name)

#  ────────────────────────────────────────────────────────────────────
#   APP INPUT
#  ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI-Powered Resume Alignment Engine", layout="wide")
st.header("AI-Powered Resume Alignment Engine")
st.write(
    "Please provide the target job description and your resume/CV to optimize it according to the job posting"
)

col1, col2 = st.columns(2)
with col1:
    description = st.text_area("Job Description:", height=200, key="desc")
    evaluate = st.button("Evaluate My Resume")
with col2:
    resume = st.text_area("Resume:", height=200, key="resume")
    optimize = st.button("Optimize My Resume")


#  ────────────────────────────────────────────────────────────────────
#   EVALUATION CHAINS
#  ────────────────────────────────────────────────────────────────────
def create_chain(template, model=llm):
    input_variables = template.count("{")
    prompt_template = PromptTemplate(template=template, input_variables=input_variables)
    return prompt_template | model | StrOutputParser()


evaluation_templates = {
    "strengths": f"{role}\n{plus}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
    "weaknesses": f"{role}\n{minus}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
    "missing_keywords": f"{role}\n{keys}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
}

evaluation_results = {
    key: create_chain(template) for key, template in evaluation_templates.items()
}

recommendations_template = f"{recommendations}\nStrengths and Weaknesses:\n{{strengths}}\n{{weaknesses}}\nMissing Keywords:\n{{missing_keywords}}"
recommendations_chain = create_chain(recommendations_template)


#  ────────────────────────────────────────────────────────────────────
#   OPTIMIZATION TEMPLATES
#  ────────────────────────────────────────────────────────────────────
def create_chain(template, input_variables, output_key, model=llm):
    prompt = PromptTemplate(template=template, input_variables=input_variables)
    return RunnableParallel(
        {
            output_key: prompt | model | StrOutputParser(),
            **{
                var: RunnablePassthrough()
                for var in input_variables
                if var != output_key
            },
        }
    )


optimization_templates = {
    "bullet_opt": f"{optimization}\n{bullet_opt}\nResume:\n{{resume}}\nJob Description:\n{{description}}\nEvaluation Report:\n{{evaluation}}",
    "key_opt": f"{optimization}\n{key_opt}\nResume:\n{{bullet_optimized}}\nJob Description:\n{{description}}\nEvaluation Report:\n{{evaluation}}",
    "output": f"{output}\nOptimized Resume:\n{{keyword_optimized}}",
    "summary": f"{summary}\nOriginal Resume:\n{{resume}}\nOptimized Resume:\n{{optimized_resume}}",
}

optimization_chain = (
    create_chain(
        optimization_templates["bullet_opt"],
        ["resume", "description", "evaluation"],
        "bullet_optimized",
    )
    | create_chain(
        optimization_templates["key_opt"],
        ["bullet_optimized", "description", "evaluation"],
        "keyword_optimized",
    )
    | create_chain(
        optimization_templates["output"], ["keyword_optimized"], "optimized_resume"
    )
)

summary_chain = create_chain(
    optimization_templates["summary"], ["resume", "optimized_resume"], "final_summary"
)


#  ────────────────────────────────────────────────────────────────────
#   STREAMLIT APP
#  ────────────────────────────────────────────────────────────────────
def run_evaluation(description, resume):
    results = {
        key: chain.invoke({"description": description, "resume": resume})
        for key, chain in evaluation_results.items()
    }
    recommendations = recommendations_chain.invoke(results)
    return [
        results["strengths"],
        results["weaknesses"],
        results["missing_keywords"],
        recommendations,
    ]


if evaluate:
    if description and resume:
        with st.spinner("Analyzing resume..."):
            strengths, weaknesses, missing_keywords, recommendations = run_evaluation(
                description, resume
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
            st.write(recommendations)
    else:
        st.warning("Please provide both resume and job description.")

if optimize:
    if description and resume:
        with st.spinner("Optimizing resume..."):
            _, weaknesses, missing_keywords, recommendations = run_evaluation(
                description, resume
            )

            evaluation = f"""Weaknesses:\n{weaknesses}\nMissing Keywords\n{missing_keywords}\nRecommendations:\n{recommendations}"""

            optimization_result = optimization_chain.invoke(
                {"resume": resume, "description": description, "evaluation": evaluation}
            )

            optimized_resume = optimization_result["optimized_resume"]

            summary_result = summary_chain.invoke(
                {"resume": resume, "optimized_resume": optimized_resume}
            )

            summary_of_changes = summary_result["final_summary"]

            st.subheader("Optimized Resume")
            st.text(optimized_resume)
            st.subheader("Summary of Changes")
            st.write(summary_result)
    else:
        st.warning("Please provide both resume and job description.")
