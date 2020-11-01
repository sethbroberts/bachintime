import streamlit as st
import pandas as pd 
import numpy as np 
import datetime
import time


def read_data():
    df = pd.read_csv('bachintime.csv')
    df = df[df['JEG CD'].notnull()]
    df.loc[:,'Date'] = df['Date'].apply(pd.to_datetime)
    df.loc[:,'Weekday'] = df['Date'].dt.weekday.map(
        {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
    )
    return df


def makegaps(x, now):
    curryr = now.year
    workyr = x['Date'].year
    yrsago = curryr - workyr
    currdt = datetime.datetime(curryr, int(x['Date'].month), int(x['Date'].day))
    x['Delta'] = ((currdt.date() - now.date()).days)
    x['Years Ago'] = yrsago
    x['Days Ago'] = ((currdt.date() - now.date()).days)
    x['Date'] = x['Date'].date()
    return x


def create_explanation(years_ago, days_ago):
    if days_ago < 0:
        explanation = f"*{years_ago} years ago, Bach would have just recently performed this ({int(-1 * days_ago)} days prior).*"
    elif days_ago > 0:
        explanation = f"*{years_ago} years ago, Bach would have been preparing to perform this in {days_ago} days.*"
    elif days_ago == 0:
        explanation = f"***Performed this day, {years_ago} years ago.***"
    else:
        explanation = ""
    if abs(days_ago) == 1:
        explanation = explanation.replace('days', 'day')
    return explanation


#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def main():
    now = datetime.datetime.now()
    df = read_data()
    df_ = df.apply(makegaps, args=(now,), axis=1)
    window = df_[
        (df_['Delta'] >= -3) & (df_['Delta'] <= 7)
    ].copy().sort_values('Delta', ascending=False).reset_index(drop=True)
    window.drop(columns=['Delta'], inplace=True)

    # sidebar
    # st.sidebar.markdown("""### About  \nThe goal of this page is to give a sense of some of 
    # J.S. Bach's day to day preoccupations at various times of the year.
    # """)
    #st.sidebar.video('https://www.youtube.com/watch?v=5o1DZPqqx-M')

    # title for page
    st.title(f"Bach In Time")

    # add header based on selected value
    st.header(f"Today is {now.date()}")

    # add in subheader and table for raw data
    st.subheader('Music Bach was thinking about this time of year:')
    for index, row in window.iterrows():
        explanation = create_explanation(row['Years Ago'], row['Days Ago'])
        st.markdown("---")
        st.markdown(f"BWV {row['BWV']}, {row['Title']}")
        st.markdown(f"Performance Date: {row['Weekday']}, {row['Date']}.  \n{explanation}")                
        st.markdown(f"CD {int(row['JEG CD'])} in complete cantatas by John Eliot Gardiner / Monteverdi Choir / English Baroque Soloists")
        half1 = f"More information: [Wikipedia]({row['Wikipedia']}), [IMSLP]({row['IMSLP']}), [Bach Digital]({row['Bach Digital']})"
        half2 = f", [Performances]({row['YouTube']}), [Translation]({row['Translation']})"
        st.markdown(half1 + half2)
    
if __name__ == '__main__':
    main()
