import pandas as pd
import numpy as np
from rake_nltk import Rake
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import altair as alt
import pandas as pd

def clean_col_names(df, columns):
	new = []
	for c in columns:
		new.append(c.lower().replace(' ','_'))
	return new

def prepare_data(df):
    # clean column names
    df.columns = clean_col_names(df, df.columns)

    # impute missing values that creeped in
    df['skills'] = df['skills'].fillna('Missing')
    df['instructors'] = df['instructors'].fillna('Missing')

    # making certain features numeric
    def make_numeric(x):
        if(x=='Missing'):
            return np.nan
        return float(x)

    df['course_rating'] = df['course_rating'].apply(make_numeric)
    df['course_rated_by'] = df['course_rated_by'].apply(make_numeric)
    df['percentage_of_new_career_starts'] = df['percentage_of_new_career_starts'].apply(make_numeric)
    df['percentage_of_pay_increase_or_promotion'] = df['percentage_of_pay_increase_or_promotion'].apply(make_numeric)

    def make_count_numeric(x):
        if 'k' in x:
            return (float(x.replace('k','')) * 1000)
        elif 'm' in x:    
            return (float(x.replace('m','')) * 1000000)
        elif 'Missing' in x:
            return (np.nan)

    df['enrolled_student_count'] = df['enrolled_student_count'].apply(make_count_numeric)

    # extract time to complete
    def find_time(x):
        l = x.split(' ')
        idx = 0
        for i in range(len(l)):
            if(l[i].isdigit()):
                idx = i 
        try:
            return (l[idx] + ' ' + l[idx+1])
        except:
            return l[idx]

    df['estimated_time_to_complete'] = df['estimated_time_to_complete'].apply(find_time)

    # split by skills
    def split_it(x):
        return (x.split(','))

    df['skills'] = df['skills'].apply(split_it)

    return df


def load_data():
	source_path1 = os.path.join("data/coursera-courses-overview.csv") 
	source_path2 = os.path.join("data/coursera-individual-courses.csv")
	df_overview = pd.read_csv(source_path1)
	df_individual = pd.read_csv(source_path2)
	df = pd.concat([df_overview, df_individual], axis=1)
	# preprocess it now
	df = prepare_data(df)

	return df

def filter(dataframe, chosen_options, feature, id):
	selected_records = []
	for i in range(1000):
		for op in chosen_options:

			if op in dataframe[feature][i]:
				selected_records.append(dataframe[id][i])
	return selected_records


def extract_keywords(df, feature):
    r = Rake()
    keyword_lists = []
    for i in range(df.shape[0]):
        descr = df[feature][i]
        r.extract_keywords_from_text(descr)
        key_words_dict_scores = r.get_word_degrees()
        keywords_string = " ".join(list(key_words_dict_scores.keys()))
        keyword_lists.append(keywords_string)
    return keyword_lists


def recommendations(df, cosine_sim, find_similar=True, how_many=5):
    
    # initialise recommended courses list
    recommended = []
    selected_course = df
    idx = selected_course.index[0]
    if(find_similar):
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending = False)
    else:
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending = True)

    if(len(score_series) < how_many):
        how_many = len(score_series)
    top_sugg = list(score_series.iloc[1:how_many+1].index)
    
    for i in top_sugg:
        qualified = df['course_name'].iloc[i]
        recommended.append(qualified)
    
    return recommended


def content_based_recommendations(df, courses):
    # filter out the courses
    df = df[df['course_name'].isin(courses)].reset_index()
    # create description keywords
    df['descr_keywords'] = extract_keywords(df, 'description')
    # instantiating and generating the count matrix
    count = CountVectorizer()
    count_matrix = count.fit_transform(df['descr_keywords'])
    # generating the cosine similarity matrix
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    # make the recommendation
    rec_courses_similar = recommendations(df, cosine_sim, True)
    temp_sim = df[df['course_name'].isin(rec_courses_similar)]
    rec_courses_dissimilar = recommendations(df, cosine_sim, False)
    temp_dissim = df[df['course_name'].isin(rec_courses_dissimilar)]
    #print(temp_sim['course_name'],'hello')
    temp_sim.to_csv('file.csv' , index=False)

def prep_for_cbr(df,skill):
	skills_avail = []
	for i in range(1000):
		skills_avail = skills_avail + df['skills'][i]
	skills_avail = list(set(skills_avail))
	skills_select = skill
	skill_filtered = None
	courses = None
	temp = filter(df, skills_select, 'skills', 'course_url')
	skill_filtered = df[df['course_url'].isin(temp)].reset_index()
	courses = skill_filtered['course_name']
	content_based_recommendations(df, courses)
    

def call_fn(skills):
    #print('here : ','\n',skills)
    df = load_data()
    prep_for_cbr(df,skills)
	
