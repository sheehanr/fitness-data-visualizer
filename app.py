import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression

def process_data(workouts_file, bodyweight_file):
    workouts_df = pd.read_csv(workouts_file)
    bodyweights_df = pd.read_csv(bodyweight_file)

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
    bodyweights_df = bodyweights_df[['date', 'weight_lbs']]
    bodyweights_df['date'] = pd.to_datetime(bodyweights_df['date'])

    # merge workout and bodyweight data
    final_df = pd.merge(workouts_df, bodyweights_df, on='date', how='outer')
    final_df.sort_values(by='date', ascending=True, inplace=True)  # sort in ascending order
    
    # rename duplicate columns
    final_df = final_df.rename(columns={
        'title': 'workout_title',
        'weight_lbs_x': 'working_weight_lbs',
        'weight_lbs_y': 'bodyweight_lbs'
    })

    # rearrange columns for logical presentation
    cols = final_df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('date')))
    final_df = final_df[cols]
    cols.insert(1, cols.pop(cols.index('bodyweight_lbs')))
    final_df = final_df[cols]