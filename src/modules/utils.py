from wordcloud import STOPWORDS, WordCloud
import PyPDF2

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


resume_stopwords = [
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday", "company", "address", "email", "phone",
    "number", "date", "year", "years", "experience", "education", "skill", "skills", "summary", 
    "objective", "responsibility", "responsibilities", "accomplishment", "accomplishments", 
    "project", "projects", "qualification", "qualifications", "certification", "certifications",
    "state", "city", "university", "college", "institute", "school", "name", "management", "month", "months"
]

def generate_wordcloud(text):
    stopwords = set(STOPWORDS).union(resume_stopwords)
    wordcloud = WordCloud(
        width=800, height=400, background_color="white", stopwords=stopwords
    ).generate(text.lower())
    return wordcloud
