import os
from io import BytesIO

import google.generativeai as genai
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.modules.nlp import preprocessing
from src.modules.utils import generate_wordcloud, read_pdf
from src.templates.prompts import (
    EVALUATION_TEMPLATES,
    OPTIMIZATION_TEMPLATES,
    recommendations_prompt,
)

load_dotenv()

#  ────────────────────────────────────────────────────────────────────
#   APP INPUT
#  ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI-Powered Resume Alignment Engine", layout="wide")
st.header("AI-Powered Resume Alignment Engine")

with st.sidebar:
    st.header("Resume/CV and Job Posting")
    st.write("Choose one input method for each:")

    # Job Description Input
    job_input_method = st.radio(
        "Job Description Input Method:", ["URL", "Text"], horizontal=True
    )
    if job_input_method == "URL":
        job_url = st.text_input("Enter job posting URL")
        if job_url:
            job_loader = WebBaseLoader(job_url)
            description = preprocessing(job_loader.load()[0].page_content, exist=True)
    else:
        description = st.text_area("Enter Job Description:", height=100)
        description = preprocessing(description, exist=True)

    # Resume Input
    resume_input_method = st.radio(
        "Resume Input Method:", ["PDF", "Text"], horizontal=True
    )
    if resume_input_method == "PDF":
        resume_file = st.file_uploader("Upload your Resume/CV (PDF)", type=["pdf"])
        if resume_file:
            pdf_contents = resume_file.read()
            resume = read_pdf(BytesIO(pdf_contents))
            resume = preprocessing(resume, exist=True)
    else:
        resume = st.text_area("Enter Resume Text:", height=100)
        resume = preprocessing(resume, exist=True)

    col1, col2 = st.columns(2)
    with col1:
        evaluate = st.button("🔎 Evaluate")
    with col2:
        optimize = st.button("🚀 Optimize")

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <p>Developed by 
                <a href="https://www.linkedin.com/in/marcocamilo">Marco-Andrés Camilo-Pietri</a>
            </p>
            <a href="https://www.linkedin.com/in/marcocamilo" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?&logo=linkedin" alt="LinkedIn" style="margin-right: 10px;">
            </a>
            <a href="https://github.com/your-github-username" target="_blank">
                <img src="https://img.shields.io/badge/GitHub-100000?&logo=github" alt="GitHub" style="margin-right: 10px;">
            </a>
            <a href="https://marcocamilo.com" target="_blank">
                <img src="https://img.shields.io/badge/Website-FF7139?&logo=Firefox-Browser&logoColor=white" alt="Website">
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

#  ────────────────────────────────────────────────────────────────────
#   INITIALIZE THE GEMINI API AND LLM
#  ────────────────────────────────────────────────────────────────────
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model_name = "gemini-1.5-flash"
llm = ChatGoogleGenerativeAI(model=model_name)


#  ────────────────────────────────────────────────────────────────────
#   EVALUATION CHAINS
#  ────────────────────────────────────────────────────────────────────
def create__evaluation_chain(template, model=llm):
    input_variables = template.count("{")
    prompt_template = PromptTemplate(template=template, input_variables=input_variables)
    return prompt_template | model | StrOutputParser()


evaluation_results = {
    key: create__evaluation_chain(template)
    for key, template in EVALUATION_TEMPLATES.items()
}

recommendations_chain = create__evaluation_chain(recommendations_prompt)


#  ────────────────────────────────────────────────────────────────────
#   OPTIMIZATION TEMPLATES
#  ────────────────────────────────────────────────────────────────────
def create_optimization_chain(template, input_variables, output_key, model=llm):
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


optimization_chain = (
    create_optimization_chain(
        OPTIMIZATION_TEMPLATES["bullet_opt"],
        ["resume", "description", "evaluation"],
        "bullet_optimized",
    )
    | create_optimization_chain(
        OPTIMIZATION_TEMPLATES["key_opt"],
        ["bullet_optimized", "description", "evaluation"],
        "keyword_optimized",
    )
    | create_optimization_chain(
        OPTIMIZATION_TEMPLATES["output"], ["keyword_optimized"], "optimized_resume"
    )
)

summary_chain = create_optimization_chain(
    OPTIMIZATION_TEMPLATES["summary"], ["resume", "optimized_resume"], "final_summary"
)


#  ────────────────────────────────────────────────────────────────────
#   HELPER FUNCTIONS
#  ────────────────────────────────────────────────────────────────────
@st.cache_data
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


#  ────────────────────────────────────────────────────────────────────
#   EVALUATION
#  ────────────────────────────────────────────────────────────────────
# if not evaluate or optimize:
#     st.write("Hello")

if evaluate:
    if description and resume:
        with st.spinner("Analyzing resume..."):
            strengths, weaknesses, missing_keywords, recommendations = run_evaluation(
                description, resume
            )

            st.subheader("Word Clouds")
            col_wc1, col_wc2 = st.columns(2)

            with col_wc1:
                st.write("Job Description")
                wordcloud_desc = generate_wordcloud(description)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_desc, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

            with col_wc2:
                st.write("Resume")
                wordcloud_resume = generate_wordcloud(resume)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_resume, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

            st.subheader("Strengths and Weaknesses")
            col_s, col_w = st.columns(2)
            with col_s:
                with st.expander("See details"):
                    st.write(strengths)
            with col_w:
                with st.expander("See details"):
                    st.write(weaknesses)

            st.subheader("Missing Keywords")
            with st.expander("See details"):
                st.write(missing_keywords)

            st.subheader("Actionable Recommendations")
            with st.expander("See details"):
                st.write(recommendations)
    else:
        st.warning("Please provide both resume and job description.")


#  ────────────────────────────────────────────────────────────────────
#   OPTIMIZATION
#  ────────────────────────────────────────────────────────────────────
if optimize:
    if description and resume:
        with st.spinner("Optimizing resume..."):
            _, weaknesses, missing_keywords, recommendations = run_evaluation(
                description, resume
            )

            evaluation = f"""Weaknesses:\n{weaknesses}\nMissing Keywords\n{missing_keywords}\nRecommendations:\n{recommendations}"""

            optimized_resume = optimization_chain.invoke(
                {"resume": resume, "description": description, "evaluation": evaluation}
            )["optimized_resume"]

            summary_of_changes = summary_chain.invoke(
                {"resume": resume, "optimized_resume": optimized_resume}
            )["final_summary"]

            st.subheader("Word Clouds")
            col_wc1, col_wc2 = st.columns(2)

            with col_wc1:
                st.write("Job Description")
                wordcloud_desc = generate_wordcloud(description)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_desc, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

            with col_wc2:
                st.write("Optimized Resume")
                wordcloud_resume = generate_wordcloud(optimized_resume)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_resume, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

            st.subheader("Optimized Resume")
            with st.expander("Preview"):
                st.write(optimized_resume)
            with st.expander("Copy resume"):
                st.markdown(f"```{optimized_resume}```")

            st.subheader("Summary of Changes")
            with st.expander("See details"):
                st.write(summary_of_changes)
    else:
        st.warning("Please provide both resume and job description.")
