import pandas as pd
import numpy as np


def poc(temp_df1):

    high_current = temp_df1["uniques"].max()
    low_current = temp_df1["uniques"].min()

    half_back_current = (high_current + low_current)/2

    temp_df1 = temp_df1.sort_values("counts", ascending=False)

    temp_df1 = temp_df1[temp_df1.counts == temp_df1.counts.max()]
    temp_df1["diff"] = abs(temp_df1["uniques"] - half_back_current)
    poc_d = list(temp_df1.sort_values(by=["diff", "uniques"])["uniques"])[0]


    return poc_d


def width_poc_fun(temp_df1, poc_d):
    w_poc = temp_df1[temp_df1["uniques"] == poc_d]["counts"]

    return int(w_poc)


def VA(temp_df1, poc_d, width_poc):

    tpo_va = round(temp_df1["counts"].sum()*0.7)

    temp_df1_2 = temp_df1.sort_values("uniques", ascending=False)

    # New way of creating value areas
    above_poc = temp_df1_2[temp_df1_2["uniques"] > poc_d]
    above_poc = above_poc.sort_values("uniques", ascending = True)
    above_poc["indx"] = np.arange(len(above_poc)) // 2 + 1

    above_poc_group = above_poc.groupby('indx')["uniques"].max()
    #above_poc_group = above_poc_group.to_frame()
    above_counts = above_poc.groupby('indx')["counts"].sum()
    #above_poc_group["counts"] = above_poc.groupby('indx')["counts"].sum()
    #above_poc_group["tpo"] = "above"


    below_poc = temp_df1_2[temp_df1_2["uniques"]< poc_d]
    below_poc = below_poc.sort_values("uniques", ascending=False)
    below_poc["indx"] = np.arange(len(below_poc)) // 2 + 1

    below_poc_group = below_poc.groupby('indx')["uniques"].max()
    #below_poc_group = below_poc_group.to_frame()
    below_counts = below_poc.groupby('indx')["counts"].sum()

    #below_poc_group["counts"] = below_poc.groupby('indx')["counts"].sum()
    #below_poc_group["tpo"] = "below"

    poc_val = False
    poc_vah = False

    if len(below_poc_group) == 0:
        below_poc_group = pd.Series(poc_d, index = [1])
        below_counts = pd.Series([0])
        #below_poc_group = pd.DataFrame({"indx": [1], "uniques":[poc_d],"counts": [0], "tpo": ["below"]})
        poc_val = True
        val_d = poc_d

    if len(above_poc_group) == 0:
        above_poc_group = pd.Series(poc_d, index = [1])
        above_counts = pd.Series([0])

        #above_poc_group = pd.DataFrame({"indx": [1], "uniques":[poc_d],"counts": [0], "tpo": ["above"]})
        poc_vah = True
        vah_d = poc_d

    tpo = width_poc
   # per_val = 0
    #c_date = df2.index
    #c_date = c_date[0+1]
    #print(c_date)

    while tpo_va > tpo:
        len_above = len(above_poc_group)
        len_below = len(below_poc_group)

        above_va = above_poc_group.iloc[0]
        above_cn = above_counts.iloc[0]


        below_va = below_poc_group.iloc[0]
        below_cn = below_counts.iloc[0]

        if (above_cn >= below_cn) | (len_below <= 1):
            tpo = tpo + above_cn

            if len_above > 1:
                above_poc_group = above_poc_group.iloc[1:]
                above_counts = above_counts.iloc[1:]


        if (below_cn > above_cn) | (len_above <= 1):
            tpo = tpo + below_cn

            if len_below > 1:
                below_poc_group = below_poc_group.iloc[1:]
                below_counts = below_counts.iloc[1:]


    if poc_vah == False:
        vah_d = above_va
    if poc_val == False:
        val_d = below_va

    return (vah_d, val_d)

def ranges_MP(list_low_day, list_high_day):


    list_ranges = []
    ranges1 = np.array([])
    temp_df1 = pd.DataFrame()

    for j in range(len(list_high_day)):
        ranges1 = np.append(ranges1, np.arange(list_low_day[j], list_high_day[j] + 0.25, 0.25 ))

    temp_df1["uniques"], temp_df1["counts"] = np.unique(ranges1, return_counts=True)


    list_ranges.append(temp_df1)

    return list_ranges

def MP_features(low_columns, high_columns):

    list_ranges_val = ranges_MP(low_columns, high_columns)

    map_list_poc = list(map(poc,list_ranges_val))

    map_width_poc = list(map(width_poc_fun, list_ranges_val, map_list_poc))

    value_areas = list(map(VA, list_ranges_val, map_list_poc, map_width_poc))

    vah, val = list(zip(*value_areas))

    df_MP = pd.DataFrame({"widthpoc_": map_width_poc,"POC_": map_list_poc, "VAH_": vah, "VAL_": val})

    #df3 = df2.append(df_MP)#, ignore_index = True)

    return df_MP

def moving_MP(live_low, live_high):

    # df2 is high - low data
    # df_mp is data from full dataframe

    list_df = []
    #let = string.ascii_uppercase[0:len(live_high)]
    let = "ABCDEFGHIJKLMNABCDEFGHIJKLMNOPQRSTUVWXabcdefghijk"
    let = let[0:len(live_high)]


    for i in range(1, len(live_low)+1):
       # let = low_columns_day[i-1][4]
       # print(let)

        df_moving = MP_features(live_low[:i], live_high[:i])
        #df_moving["index"] = df2.index
        #df_moving = df_moving.set_index("index")


        list_df.append(df_moving)

    for i in range(len(list_df)):
        letter = let[i]

        list_df[i].columns = list_df[i].columns.str.replace('_', f'_{letter}')


    return list_df



def mp_chart(low_list_va, high_list_va,current_day, day_night="day", step=4, time_location="07:30", va_color="red", poc_color ="green"):
  '''
  low: list of low values
  high: list of high values
  day_night: what MP are you displaying
  step of the market profile
  current_day: current day to create the chart
  time_location: MP location

  return a figure data to place inside plotly chart
  '''
  if day_night == "day":
    c_tpo = 'ABCDEFGHIJKLMN'
  else:
    c_tpo = "ABCDEFGHIJKLMNOPQRSTUVWXabcdefghijk"


  import MP_Functions as mp
  rec = {}
  mp_ind = np.arange(max(high_list_va), min(low_list_va), -step) # from high to low with 4 points step
  for val in mp_ind:
    rec[str(val)] = ''
    for name, high, low in zip(list(c_tpo), high_list_va, low_list_va):
      if val<=high and val>=low:
        rec[str(val)] = rec[str(val)] + name

  rec = pd.Series(rec)
  rec.str.len()
  recs = pd.DataFrame([rec.index, rec]).T
  recs.columns = columns=['price', 'tpo']
  recs['price'] = recs['price'].astype('float')
  recs['time'] = f'{str(current_day)} {time_location}' # set all to 6:30 so it starts at the same hour visually purpose
  recs['time'] = pd.to_datetime(recs['time'])

  mp_feat = mp.MP_features(low_list_va, high_list_va)

  vah, val, poc = mp_feat['VAH_'][0], mp_feat['VAL_'][0], mp_feat['POC_'][0]
  recs['color'] = np.where((recs['price']<=vah)&(recs['price']>=val), va_color, "white") # color inside the value areas
  arr = np.asarray(recs['price'])
  i = (np.abs(arr - poc)).argmin()
  poc_val = arr[i]
  recs['color'] = np.where(recs['price']==poc_val, poc_color, recs['color']) # get POC
  master_recs = pd.DataFrame()
  master_recs = master_recs.append(recs)

  master_recs['Point'] = np.where(master_recs['color']==poc_color, master_recs['price'].astype('str')+' (POC)',
                                np.where(master_recs['color']==va_color, master_recs['price'].astype('str')+' (Value area)',
                                master_recs['price']))

  fig = go.Scatter(x=master_recs['time'], y=master_recs['price'], mode="text", text=master_recs['tpo'], textfont=dict(family="verdana", size=5, color=master_recs['color']),
                         textposition='top right', hovertext=master_recs['Point'], name='Market Profile Night')


  return fig
