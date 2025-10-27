import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression

def process_data(workouts_file, bodyweight_file):
    workouts_df = pd.read_csv(workouts_file)
    bodyweight_df = pd.read_csv(bodyweight_file)

    # keep only relevant strength training exercises
    workouts_df = workouts_df.drop(['description', 'exercise_notes'], axis=1)
    workouts_df = workouts_df[workouts_df['distance_miles'].isnull()]
    workouts_df = workouts_df[workouts_df['duration_seconds'].isnull()]
    workouts_df = workouts_df.drop(['superset_id', 'distance_miles', 'duration_seconds'], axis=1)

    # keep only bodyweight data
    weight_df = weight_df[['date', 'weight_lbs']]