# Import necessary libraries
import pandas as pd
import re
import warnings

# Ignore UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)


# Load course data
courses_df = pd.read_csv('F:\\test bot\data\coursera-courses.csv')


# define a regular expression to find numbers in the text
pattern = r'\d+\.?\d*'

# create a new column to store the extracted numbers
courses_df['numbers'] = courses_df['estimated_time_to_complete'].apply(lambda x: re.findall(pattern, x))

# if you want to store the numbers as floats instead of strings, you can convert them
courses_df['numbers'] = courses_df['numbers'].apply(lambda x: [int(n) for n in x])

for i in range(0,len(courses_df)):
  if(len(courses_df['numbers'][i])==0):  
    courses_df['numbers'][i].append(10)
  courses_df.loc[:,'numbers'][i]=courses_df['numbers'][i][0]
  #print(courses_df['numbers'][i])

word="months"
for i in range(0,len(courses_df)):
  if word in courses_df['estimated_time_to_complete'][i]:
    courses_df.loc[:,'numbers'][i]=courses_df['numbers'][i]*20
#print(courses_df['numbers'])

# Define the rules for course recommendation
def recommend_courses(difficulty, course_type, skill, duration):
    
    # Rule 1: If the user is looking for an introductory course, recommend Beginner level courses
    if difficulty == 'Beginner':
        recommended_courses = courses_df[courses_df['course_difficulty'] == 'Beginner']
        #print("beginner")

        
    # Rule 2: If the user is looking for a more advanced course, recommend Intermediate or Advanced level courses
    elif difficulty == 'Advanced':
        recommended_courses = courses_df[courses_df['course_difficulty'].isin(['Intermediate', 'Advanced'])]
        #print("Advanced")
    
     #Rule 3: If the user is interested in a specific course type, recommend courses in that category
    if course_type:
        recommended_courses = recommended_courses[courses_df['learning_product_type'] == course_type]
        #print("course type")

    
    # Rule 4: If the user is looking to improve a specific set of skills, recommend courses with those keywords
    if skill:
        relevant_courses = courses_df[courses_df['skills'].apply(lambda x: any([skill in x for skill in skills]))]
        recommended_courses = relevant_courses
        #print("skill")
        
    # Rule 5: If the user is looking for a course with a specific duration, recommend courses within that range
    if duration:
         duration_min, duration_max = duration
    #     courses_df['estimated_time_to_complete'] = courses_df['estimated_time_to_complete'].astype(str)
    #     courses_df['estimated_time_to_complete'] = courses_df['estimated_time_to_complete'].fillna('')
         recommended_courses = recommended_courses[courses_df['numbers']>= duration_min]
         recommended_courses = recommended_courses[courses_df['numbers'] <= duration_max]
    
    # If no rules match, recommend top rated courses
    else:
        recommended_courses = courses_df.sort_values(by='course_rating', ascending=False).head(10)

    
    recommended_courses.to_csv('output.csv', index=False)
    
    return recommended_courses['course_name'].tolist()

# Test the course recommendation function
#difficulty = 'Advanced'
#course_type = 'SPECIALIZATION'
#skills = ['Python', 'Machine Learning']
#duration = (4, 8)

difficulty = input('Enter Difficulty?\n')
course_type = input('Enter Course type?\n')
skills=list(input('Enter the skills: ').strip().split(','))
min = input('Enter min Duration?\n')
max = input('Enter max Duration?\n')
duration=(int(min),int(max))
print(skills)


recommended_courses = recommend_courses(difficulty, course_type, skills, duration)
print(' ')
print('**RECOMMENDED COURSES**:', recommended_courses)
print(' ')