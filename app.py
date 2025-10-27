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

    # convert time related columns to pandas datetime objects
    workouts_df['start_time'] = pd.to_datetime(workouts_df['start_time'])
    workouts_df['end_time'] = pd.to_datetime(workouts_df['end_time'])

    # create category called date based on start_time and convert to datetime
    workouts_df['date'] = workouts_df['start_time'].dt.date
    workouts_df['date'] = pd.to_datetime(workouts_df['date'])

    # bring date column to front of dataset
    cols = workouts_df.columns.tolist()
    cols.insert(1, cols.pop(cols.index('date')))
    workouts_df = workouts_df[cols]

    # keep only bodyweight data and convert date to datetime object
    weight_df = weight_df[['date', 'weight_lbs']]
    weight_df['date'] = pd.to_datetime(weight_df['date'])