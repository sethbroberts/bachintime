import streamlit as st
import pandas as pd 
import numpy as np 
import datetime
import time
import pytz


def read_data():
    df = pd.read_csv('bachintime.csv')
    df = df[df['JEG CD'].notnull()]
    df.loc[:,'Date'] = df['Date'].apply(pd.to_datetime)
    df.loc[:,'Weekday'] = df['Date'].dt.weekday.map(
        {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
    )
    return df


def read_life():
    df = pd.read_csv('bachlife.csv', header=None)
    df.columns = ['date type', 'year', 'dt', 'event']
    df.loc[:,'Date'] = (df['year'].astype(str) + ' ' + df['dt']).apply(
        pd.to_datetime, format='%Y %b %d'
    )
    df.loc[:,'day'] = df['Date'].dt.dayofyear
    df = df[['date type', 'Date', 'year', 'day', 'event']]
    return df


def makegaps(x, now):
    curryr = now.year
    workyr = x['Date'].year
    yrsago = curryr - workyr
    currdt = datetime.datetime(curryr, int(x['Date'].month), int(x['Date'].day))
    x['Years Ago'] = yrsago
    x['Days Ago'] = ((currdt.date() - now.date()).days)
    x['Date'] = x['Date'].date()
    return x


def create_explanation(years_ago, days_ago):
    if days_ago < 0:
        explanation = f"{years_ago} years ago, Bach would have just recently performed this ({int(-1 * days_ago)} days prior)."
    elif days_ago > 0:
        explanation = f"{years_ago} years ago, Bach would have been preparing to perform this in {days_ago} days."
    elif days_ago == 0:
        explanation = f"Performed this day, {years_ago} years ago."
    else:
        explanation = ""
    if abs(days_ago) == 1:
        explanation = explanation.replace('days', 'day')
    return explanation


def create_explanation_life(date_type, years_ago, days_ago, event):
    if date_type=='exact':
        if days_ago < 0:
            explanation = f"{years_ago} years and {int(-1 * days_ago)} days ago"
        elif days_ago > 0:
            explanation = f"{years_ago} years ago, upcoming in {days_ago} days"
        elif days_ago == 0:
            explanation = f"{years_ago} years ago on this date"
        else:
            explanation = ""
        if abs(days_ago) == 1:
            explanation = explanation.replace('days', 'day')
    elif date_type=='approx':
        explanation = f"{years_ago} years ago, around this time"
    return explanation

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

timeZ_Ny = pytz.timezone('America/New_York')
now = datetime.datetime.now(timeZ_Ny)

# read in & process performance data
df = read_data()
df_ = df.apply(makegaps, args=(now,), axis=1)
window = df_[
    (df_['Days Ago'] >= -3) & (df_['Days Ago'] <= 7)
].copy().sort_values(
    'Days Ago', ascending=False
).reset_index(drop=True)

# read in & process life event data
life = read_life()
life_ = life.apply(makegaps, args=(now,), axis=1)
window2 = life_[
    (life_['Days Ago'] >= -10) & (life_['Days Ago'] <= 10)  ##
].copy().sort_values(
    'Days Ago', ascending=False
).reset_index(drop=True)

# title for page
st.title(f"Bach In Time")

# add header based on selected value
nowdate = now.date()
st.header(f"Today is {nowdate.day} {nowdate.strftime('%B')} {nowdate.year}")

c = st.container()
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")

# add in subheader and table for raw data
with st.container():
    st.subheader('Music Bach was thinking about this time of year:')
    for index, row in window.iterrows():
        explanation = create_explanation(row['Years Ago'], row['Days Ago'])
        st.markdown("---")
        st.markdown(f"BWV {row['BWV']}, {row['Title']}")
        st.markdown(f"Performance Date: {row['Weekday']}, {row['Date'].day} {row['Date'].strftime('%B')} {row['Date'].year}.  \n*{explanation}*")
        st.markdown(f"CD {int(row['JEG CD'])} in complete cantatas by John Eliot Gardiner / Montiverdi Choir / English Baroque Soloists")
        st.markdown(f"More information: [Wikipedia]({row['Wikipedia']}), [IMSLP]({row['IMSLP']}), [Bach Digital]({row['Bach Digital']})")
    
c = st.container()
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")
c.markdown(" ")


# add in subheader and table for raw data
with st.container():
    st.subheader('Bach life events around this time of year:')
    for index, row in window2.iterrows():
        explanation = create_explanation_life(row['date type'], row['Years Ago'], row['Days Ago'], row['event'])
        st.markdown("---")
        if row['date type']=='approx':
            st.markdown(f"{row['Date'].strftime('%B')} {row['Date'].year} ({explanation}):")
            st.markdown(f"*{row['event']}*")
        elif row['date type']=='exact':
            st.markdown(f"{row['Date'].day} {row['Date'].strftime('%B')} {row['Date'].year} ({explanation}):")
            st.markdown(f"*{row['event']}*")
