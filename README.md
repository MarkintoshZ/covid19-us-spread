# Covid-19 US Spread
A geographic-spread model of Covid-19 virus for all counties in the United States using population data and commute flows from US Census.

Currently incomplete but the general idea is layed out

The source of COVID-19 data is a great [website](https://coronavirus.1point3acres.com/?from=groupmessage&isappinstalled=0) made by [1Point3Acres](https://www.1point3acres.com)

# Demo
<img src='docs/screen_shot_0.jpg'></img>
[Online Demo](https://covid19-spread.herokuapp.com)\
or\
To run it yourself:
```
git clone git@github.com:MarkintoshZ/covid19-us-spread.git
pip install -r requirements.txt
python model/spread.py
streamlit run view_trail.py
```

You can modify the settings.ini file to change the parameters for better results

You can download new data by running
```
python data/virus_data_pipeline/download.py
```

# Welcome to contribute!
