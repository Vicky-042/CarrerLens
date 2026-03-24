COURSE_DATABASE = [
    {"skill": "python",           "title": "Python for Everybody",                "platform": "Coursera",  "url": "https://coursera.org/learn/python"},
    {"skill": "machine learning", "title": "Machine Learning Specialization",      "platform": "Coursera",  "url": "https://coursera.org/specializations/machine-learning-introduction"},
    {"skill": "sql",              "title": "SQL for Data Science",                 "platform": "Coursera",  "url": "https://coursera.org/learn/sql-data-science"},
    {"skill": "deep learning",    "title": "Deep Learning Specialization",         "platform": "Coursera",  "url": "https://coursera.org/specializations/deep-learning"},
    {"skill": "docker",           "title": "Docker for Beginners",                 "platform": "NPTEL",     "url": "https://nptel.ac.in"},
    {"skill": "aws",              "title": "AWS Cloud Foundations",                "platform": "AWS Free",  "url": "https://aws.amazon.com/training/"},
    {"skill": "react",            "title": "React - The Complete Guide",           "platform": "Udemy",     "url": "https://udemy.com/course/react-the-complete-guide"},
    {"skill": "javascript",       "title": "JavaScript Algorithms & Structures",   "platform": "freeCodeCamp", "url": "https://freecodecamp.org"},
    {"skill": "node",             "title": "Node.js Developer Course",             "platform": "Udemy",     "url": "https://udemy.com/course/the-complete-nodejs-developer-course"},
    {"skill": "django",           "title": "Django for Beginners",                 "platform": "NPTEL",     "url": "https://nptel.ac.in"},
    {"skill": "flask",            "title": "REST APIs with Flask and Python",      "platform": "Udemy",     "url": "https://udemy.com/course/rest-api-flask-and-python"},
    {"skill": "git",              "title": "Version Control with Git",             "platform": "Coursera",  "url": "https://coursera.org/learn/version-control-with-git"},
    {"skill": "linux",            "title": "Linux Command Line Basics",            "platform": "Udacity",   "url": "https://udacity.com/course/linux-command-line-basics--ud595"},
    {"skill": "mongodb",          "title": "MongoDB Basics",                       "platform": "MongoDB University", "url": "https://university.mongodb.com"},
    {"skill": "postgresql",       "title": "Databases and SQL",                    "platform": "Stanford Online", "url": "https://online.stanford.edu"},
    {"skill": "tensorflow",       "title": "TensorFlow Developer Certificate",     "platform": "Coursera",  "url": "https://coursera.org/professional-certificates/tensorflow-in-practice"},
    {"skill": "kubernetes",       "title": "Kubernetes for Beginners",             "platform": "KodeKloud", "url": "https://kodekloud.com"},
    {"skill": "data analysis",    "title": "Data Analysis with Python",            "platform": "Coursera",  "url": "https://coursera.org/learn/data-analysis-with-python"},
    {"skill": "agile",            "title": "Agile Development Specialization",     "platform": "Coursera",  "url": "https://coursera.org/specializations/agile-development"},
    {"skill": "java",             "title": "Java Programming Masterclass",         "platform": "Udemy",     "url": "https://udemy.com/course/java-the-complete-java-developer-course"},
]

def get_recommendations(missing_keywords: list) -> list:
    """
    For each missing skill, find a matching course.
    Returns max 6 recommendations to keep UI clean.
    """
    recommendations = []
    seen_titles = set()

    for skill in missing_keywords:
        skill_lower = skill.lower()
        for course in COURSE_DATABASE:
            if course["skill"] in skill_lower or skill_lower in course["skill"]:
                if course["title"] not in seen_titles:
                    recommendations.append({
                        "for_skill": skill,
                        **course
                    })
                    seen_titles.add(course["title"])
                    break

    return recommendations[:6]