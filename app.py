import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression

rpe_chart = {
    10: {1: 1.0, 2: 0.955, 3: 0.922, 4: 0.892, 5: 0.863, 6: 0.837, 7: 0.811, 8: 0.786, 9: 0.762, 10: 0.739, 11: 0.707, 12: 0.68, 13: 0.653, 14: 0.626, 15: 0.599},
    9.5: {1: 0.9775, 2: 0.9385, 3: 0.907, 4: 0.8775, 5: 0.85, 6: 0.824, 7: 0.7985, 8: 0.774, 9: 0.7505, 10: 0.723, 11: 0.6935, 12: 0.6665, 13: 0.6395, 14: 0.6125, 15: 0.5855},
    9: {1: 0.955, 2: 0.922, 3: 0.892, 4: 0.863, 5: 0.837, 6: 0.811, 7: 0.786, 8: 0.762, 9: 0.739, 10: 0.707, 11: 0.68, 12: 0.653, 13: 0.626, 14: 0.599, 15: 0.572},
    8.5: {1: 0.9385, 2: 0.907, 3: 0.8775, 4: 0.85, 5: 0.824, 6: 0.7985, 7: 0.774, 8: 0.7505, 9: 0.723, 10: 0.6935, 11: 0.6665, 12: 0.6395, 13: 0.6125, 14: 0.5855, 15: 0.5585},
    8: {1: 0.922, 2: 0.892, 3: 0.863, 4: 0.837, 5: 0.811, 6: 0.786, 7: 0.762, 8: 0.739, 9: 0.707, 10: 0.68, 11: 0.653, 12: 0.626, 13: 0.599, 14: 0.572, 15: 0.545},
    7.5: {1: 0.907, 2: 0.8775, 3: 0.85, 4: 0.824, 5: 0.7985, 6: 0.774, 7: 0.7505, 8: 0.723, 9: 0.6935, 10: 0.6665, 11: 0.6395, 12: 0.6125, 13: 0.5855, 14: 0.5585, 15: 0.5315},
    7: {1: 0.892, 2: 0.863, 3: 0.837, 4: 0.811, 5: 0.786, 6: 0.762, 7: 0.739, 8: 0.707, 9: 0.68, 10: 0.653, 11: 0.626, 12: 0.599, 13: 0.572, 14: 0.545, 15: 0.518},
    6: {1: 0.863, 2: 0.837, 3: 0.811, 4: 0.786, 5: 0.762, 6: 0.739, 7: 0.707, 8: 0.68, 9: 0.653, 10: 0.626, 11: 0.599, 12: 0.572, 13: 0.545, 14: 0.518, 15: 0.491}
}

def calculate_e1rm(row):
    try:
        # obtain the information about the set necessary for calculating an estimated one rep max
        working_weight = row['working_weight_lbs']
        reps = row['reps']
        rpe = row['rpe']

        # disregard sets with over 15 reps since they are not accounted for in the chart and are irrelevant for determining strength
        if reps > 15:
            return None

        # return the estimated one rep max rounded to 1 decimal point
        percentage = rpe_chart[rpe][reps]
        return round(working_weight / percentage, 1)
    
    # return nothing when values are missing
    except (KeyError, TypeError):
        return None

def process_data(workouts_file, bodyweights_file):
    workouts_df = pd.read_csv(workouts_file)
    bodyweights_df = pd.read_csv(bodyweights_file)

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
    processed_df = pd.merge(workouts_df, bodyweights_df, on='date', how='outer')
    processed_df.sort_values(by='date', ascending=True, inplace=True)  # sort in ascending order
    
    # rename duplicate columns
    processed_df = processed_df.rename(columns={
        'title': 'workout_title',
        'weight_lbs_x': 'working_weight_lbs',
        'weight_lbs_y': 'bodyweight_lbs'
    })

    # rearrange columns for logical presentation
    cols = processed_df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('date')))
    processed_df = processed_df[cols]
    cols.insert(1, cols.pop(cols.index('bodyweight_lbs')))
    processed_df = processed_df[cols]

    # add estimated 1-rep max column with value
    processed_df['estimated_1rm'] = processed_df.apply(calculate_e1rm, axis=1)

    # fill in gaps in weight records with a straight line between existing values and rearrange columns
    processed_df['bodyweight_interpolated'] = processed_df['bodyweight_lbs'].interpolate()
    cols = processed_df.columns.tolist()
    cols.insert(2, cols.pop(cols.index('bodyweight_interpolated')))
    processed_df = processed_df[cols]

    return processed_df

def visualize_bodyweight(processed_df):
    # create a line chart of interpolated data
    bodyweight_chart = px.line(processed_df, 'date', 'bodyweight_interpolated', title="Bodyweight Over Time", labels={'date': 'Date', 'bodyweight_interpolated': 'Bodyweight (lbs)'})

    # recorded values are dots and laid over interpolated chart
    bodyweight_dots = px.scatter(processed_df, 'date', 'bodyweight_lbs')
    bodyweight_dots.update_traces(
        marker=dict(size=5, opacity=0.5, color="gray")  # make dots more readable
    )
    bodyweight_chart.add_trace(bodyweight_dots.data[0])
    
    # date shown every 2 months in mm/yyyy format
    bodyweight_chart.update_layout(
        xaxis_tickformat="%m/%Y",
        xaxis_dtick="M2"
    )
    
    return bodyweight_chart

def visualize_e1rm(processed_df, selected_exercise):
    selected_exercise_df = processed_df[processed_df['exercise_title'] == selected_exercise]
    e1rm_chart = px.line(selected_exercise_df, 'date', 'estimated_1rm', title="Estimated 1RM Over Time", labels={'date': 'Date', 'estimated_1rm': 'Estimated 1RM (lbs)'})
    
    # date shown every 2 months in mm/yyyy format
    e1rm_chart.update_layout(
        xaxis_tickformat="%m/%Y",
        xaxis_dtick="M2"
    )

def main():
    st.title("Fitness Data Visualizer")
    workouts_file = st.file_uploader("Upload workout data (.CSV)")
    bodyweights_file = st.file_uploader("Upload bodyweight data (.CSV)")

    if workouts_file is not None and bodyweights_file is not None:
        processed_df = process_data(workouts_file, bodyweights_file)
        
        st.header("Bodyweight Visualization")
        bodyweight_chart = visualize_bodyweight(processed_df)
        st.plotly_chart(bodyweight_chart)
        
        st.header("Strength Visualization")
        e1rm_chart = visualize_e1rm(processed_df)
        st.plotly_chart(e1rm_chart)

if __name__ == "__main__":
    main()