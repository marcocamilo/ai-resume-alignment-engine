role = """
You are an experienced Human Resources Manager, specializing in analyzing resumes and providing recommendations that help job seekers optimize their resumes. Your task is to evaluate the alignment between the provided resume and job description, and provide an expert's evaluation on whether the candidate had the best profile for the role. Please complete the following tasks.
"""

plus_minus = """
1. List of Strengths and Weaknesses 

Create a list of the resume's strengths and weaknesses linked to the job description. Under each strength, give a concrete example or observation found in the resume demonstrating that strength. Under each weakness, give a concrete example of how an enhancement would look like.

For each item in the list, use the following format: 

**Strengths**
- '[strength]: one-sentence brief explanation.' 
    - Example: concrete example
**Weakness**
- '[weakness]: one-sentence brief explanation.' 
    - Example: concrete example

Return only the output, without a heading introducing it.
"""

plus = """
1a. List of Strengths

Create a list of the resume's strengths linked to the job description. Under each strength, give a concrete example or observation found in the resume demonstrating that strength.

For each item in the list, use the following format: 

- '[strength]: one-sentence brief explanation.' 
    - Example: concrete example

Return only the output, without a heading introducing it.
"""

minus = """
1b. List of Weaknesses

Create a list of the resume's areas of improvement linked to the job description. Under each weakness, give a concrete example or observation found in the resume demonstrating that strength.

For each item in the list, use the following format: 

- '[weakness]: one-sentence brief explanation.' 
    - Example: concrete example

Return only the output, without a heading introducing it.
"""

keys = """
2. Missing Keywords

List the keywords from the job description that are missing in the resume, specially skills, tools/frameworks, and behavioral adjectives. Provide only the keywords and phrases, without explanations. Use separate bullet points to breakdown list of keywords. Return only the output, without a heading introducing it.
"""

recommendations = """
3. Actionable Recommendations

Provide a series of actionable recommendations to enhance elements of the resume. You will base your recommendations exclusively on the strengths & weaknesses, and missing keywords identified in observations cited below. Include suggestions for enhancing bullet points, adding relevant skills, and incorporating missing keywords to optimize the resume. Ensure the recommendations are specific, practical, and aimed at making the resume as competitive as possible. 

Provide each recommendation in the following format: 

- '[actionable recommendation]: brief explanation.' 
    - Concrete example(s)

Return only the output, without a heading introducing it.
"""

recommendations_prompt = f"{recommendations}\nStrengths and Weaknesses:\n{{strengths}}\n{{weaknesses}}\nMissing Keywords:\n{{missing_keywords}}"

optimization = """
You are an experienced Human Resources Manager, specializing in rewriting resumes to optimize their alignment with job descriptions. Your task is to enhance the alignment between the provided resume and job description. To achieve this, you will modify the resume's content at different levels following the evaluation report provided below. Please complete the following tasks.
"""

bullet_opt = """
1. Bullet point optimization: 

Based on the evaluation report, you will focus only on the resume's project and experience sections and optimize each bullet point. For each bullet point, optimize the statements following these guidelines:

    • Strong Action Verbs: begin each bullet point with an action verb
    • Quantifiable metrics: use numbers or percentages in each bullet point to quantify achievements.
    • Domain Knowledge: put the specific hard skills and platform-based skills throughout my resume to show that the candidate fits qualifications states in the job description.
    • Impact Statements: include impact statements to showcase whether the candidate improved, optimized, or increased 'XYZ.'
    • Sprinkle soft skills: use more broad, simple statements, these are relative to collaboration, providing recommendations, and identifying solutions to potential problems.
    • Bold Impact and Technical Skills: Highlight key results and relevant technical skills to ensure they stand out.

Each bullet point must meet all five guidelines, but in particular, the use of strong action verbs and quantificable metrics. Enhance each bullet point further by working the missing keywords and skills mentioned in the evaluation into the bullet points, to help with the ATS.

Modify only the project and experience sections. Ensure these modifications reflect the evaluation's feedback and stregnthen the alignment between the bullet points and the job description. Return the full resume with the enhanced bullet points in the projects and experience sections. Return only the output, without a heading introducing it.
"""

key_opt = """
2. Skills and keyword optimization:

Based on evaluation report, integrate the missing keywords and skills into the skills section of the resume. Ensure the skills section remains concise and relevant to the job description. Return the full resume with the optimized skills section. Return only the output, without a heading introducing it.
"""

output = """
3. Observe formatting and length considerations

Adjust and optimize the entire resume content to ensure it does not exceed the length of the original resume, as the updated resume should fit within the same space as the original.

Bare in mind the following limitations:
    • You are not allowed to add or remove projects or experiences other than the ones in the resume.
    • You cannot exceed the original length of the resume. This is because the original resume already fits in one page. You must be mindful of the volume of text, ensuring your version has a similar length to the original version.
    • Do not include an objective/professional summary. It is not used anymore.

Return the optimized resume using the same format as provided in the input. Return only the output, without a heading introducing it.
"""

summary = """Return a summary of the changes made. Return only the output, without a heading introducing it."""

EVALUATION_TEMPLATES = {
    "strengths": f"{role}\n{plus}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
    "weaknesses": f"{role}\n{minus}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
    "missing_keywords": f"{role}\n{keys}\nJob Description:\n{{description}}\nResume:\n{{resume}}",
}

OPTIMIZATION_TEMPLATES = {
    "bullet_opt": f"{optimization}\n{bullet_opt}\nResume:\n{{resume}}\nJob Description:\n{{description}}\nEvaluation Report:\n{{evaluation}}",
    "key_opt": f"{optimization}\n{key_opt}\nResume:\n{{bullet_optimized}}\nJob Description:\n{{description}}\nEvaluation Report:\n{{evaluation}}",
    "output": f"{output}\nOptimized Resume:\n{{keyword_optimized}}",
    "summary": f"{summary}\nOriginal Resume:\n{{resume}}\nOptimized Resume:\n{{optimized_resume}}",
}
