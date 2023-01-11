from abc import ABC
from html.parser import HTMLParser
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import json


followers_file_html = "/Users/christophergillam/Downloads/squarelightjeep_20220730/followers_and_following/followers.html"
following_file_html = "/Users/christophergillam/Downloads/squarelightjeep_20220730/followers_and_following/following.html"
postInfo_file_html = "/Users/christophergillam/Downloads/squarelightjeep_20220730/past_instagram_insights/posts.html"

followers_file_json = "/Users/christophergillam/Desktop/squarelightjeep_20221208/followers_and_following/followers.json"
following_file_json = "/Users/christophergillam/Desktop/squarelightjeep_20221208/followers_and_following/following.json"
postInfo_file_json = "/Users/christophergillam/Desktop/squarelightjeep_20221208/past_instagram_insights/posts.json"


def get_user_names_from_html(html_file_str):
    f = open(html_file_str, "r")
    data = f.read()
    un_list = []

    while data:
        s = data.find("www.instagram.com")
        if s > 0:
            e = data[s:].find('"')
            full_url = data[s:s + e]
            u = full_url.find('/')
            un = full_url[u + 1:]
            data = data[s + e:]
            un_list.append(un)
        else:
            break

    f.close()
    return un_list


def get_user_names_from_json(json_file_str, b_follower_file):
    #df = pd.read_json(json_file_str)
    if b_follower_file:
        relationship = 'relationships_followers'
    else:
        relationship = 'relationships_following'
    with open(json_file_str, 'r') as f:
        data = json.loads(f.read())

    # Normalizing data
    df = pd.json_normalize(data,
                           record_path=[relationship, 'string_list_data'],
                           #meta = ['string_list_data','href', 'value', 'timestamp']
                           #meta = ["string_list_data"]
                           )
    #df = pd.read_json(json_file_str)
    return df['href'].tolist()


def get_followers_not_following(b_html_file, grouping_count=0):
    if b_html_file:
        followers_list = get_user_names_from_html(followers_file_html)
        following_list = get_user_names_from_html(following_file_html)
    else:
        followers_list = get_user_names_from_json(followers_file_json, True)
        following_list = get_user_names_from_json(following_file_json, False)

    not_following_list = []
    for following in following_list:
        if following not in followers_list:
            not_following_list.append(following)

    print("You have " + str(len(followers_list)) + " followers.")
    print("You are following " + str(len(following_list)) + " people.")
    print("You are following " + str(len(not_following_list)) + " people who are not following you.")
    print(not_following_list)

    fw = open("not_following.txt", 'w')
    for not_following in not_following_list:
        fw.write(not_following + '\n')

    grouping = 16
    grouping_count = 3
    sub_list = not_following_list[(grouping_count-1)*grouping: grouping_count*grouping]
    print(len(sub_list))
    for nf in sub_list:
        print(nf)

# get_followers_not_following(False)


class PostHTMLParser(HTMLParser, ABC):
    df = None
    d = None
    next_data = None
    div_cntr = 0

    def handle_starttag(self, tag, attr):
        # print("Encountered a start tag and attribute:", tag, attr)
        if 'div' == tag:
            if attr and 'class' == attr[0][0]:
                if 'pam _3-95 _2ph- _a6-g uiBoxWhite noborder' == attr[0][1]:
                    if self.d:
                        assert 0
                    else:
                        self.d = {}
                        self.div_cntr = 1
            elif self.div_cntr:
                self.div_cntr += 1
        elif 'img' == tag or 'video' == tag:
            if self.d is not None and attr and 'src' == attr[0][0]:
                self.d['Media File'] = attr[0][1]

    def handle_endtag(self, tag):
        if 'div' == tag and self.div_cntr:
            self.div_cntr -= 1
            if 0 == self.div_cntr:
                df_new = pd.DataFrame(self.d, index=[0])
                self.df = pd.concat([self.df, df_new])
                self.d = None
        elif 'img' == tag or 'video' == tag:
            if self.d is not None:
                self.next_data = 'Caption'

    def handle_data(self, data):
        if self.d:
            if self.next_data:
                if "Creation Timestamp" == self.next_data:
                    dt_obj = datetime.strptime(data, '%b %d, %Y, %H:%M %p')
                    dt_obj = dt_obj.replace(hour=dt_obj.hour + 3)
                    self.d['DateTime'] = dt_obj
                    self.d['Date'] = dt_obj.date()
                    self.d['Time'] = dt_obj.time()
                self.d[self.next_data] = data
                self.next_data = None
            else:
                self.next_data = data

    def get_dataframe(self):
        return self.df


class PostDataFrame:
    def __init__(self, df):
        self.df = df

    @classmethod
    def create_from_html(cls, html_file):
        with open(html_file, "r") as f:
            data = f.read()
            parser = PostHTMLParser()
            parser.feed(data)
            df = parser.df
            df.fillna('0', inplace=True)
            df.replace('--', inplace=True)
            return PostDataFrame(df)

    @classmethod
    def create_from_json(cls, json_file_str):
        with open(json_file_str, 'r') as f:
            data = json.loads(f.read())

        # Normalizing data
        df = pd.json_normalize(data, 'organic_insights_posts')
        df.replace('', np.nan, inplace=True)
        df.dropna(inplace=True, how='all', axis=1)  # Remove empty columns
        df.replace('--', '0', inplace=True)
        df.replace(np.nan, '0', inplace=True)
        df.drop(['string_map_data.Profile Visits.timestamp',
                 'string_map_data.Impressions.timestamp',
                 'string_map_data.Follows.timestamp',
                 'string_map_data.Accounts reached.timestamp',
                 'string_map_data.Saves.timestamp',
                 'string_map_data.Likes.timestamp',
                 'string_map_data.Comments.timestamp',
                 'string_map_data.Shares.timestamp',
                 'string_map_data.Website taps.timestamp',
                 'string_map_data.Email button taps.timestamp',
                 'string_map_data.Product Page Views.timestamp',
                 'string_map_data.Product Button Clicks.timestamp',
                 'string_map_data.Creation Timestamp.timestamp'], axis=1, inplace=True)
        df.rename(columns={'media_map_data.Media Thumbnail.uri': 'Photo Filename',
                           'media_map_data.Media Thumbnail.creation_timestamp': 'Timestamp',
                           'media_map_data.Media Thumbnail.media_metadata.photo_metadata.exif_data': 'Photo Data',
                           'media_map_data.Media Thumbnail.title': 'Post Caption',
                           'string_map_data.Profile Visits.value': 'Profile Visits',
                           'string_map_data.Impressions.value': 'Impressions',
                           'string_map_data.Follows.value': 'Follows',
                           'string_map_data.Accounts reached.value': 'Accounts reached',
                           'string_map_data.Saves.value': 'Saves',
                           'string_map_data.Likes.value': 'Likes',
                           'string_map_data.Comments.value': 'Comments',
                           'string_map_data.Shares.value': 'Shares',
                           'string_map_data.Website taps.value': 'Website clicks',
                           'media_map_data.Media Thumbnail.media_metadata.video_metadata.exif_data': 'Video Data',
                           'string_map_data.Email button taps.value': 'Email clicks',
                           'media_map_data.Media Thumbnail.product_tags': 'Product Tags',
                           'string_map_data.Product Page Views.value': 'Product Page Views',
                           'string_map_data.Product Button Clicks': 'Product Button Clicks'
                           }, inplace=True)
        df['DateTime'] = list(map(datetime.fromtimestamp, df['Timestamp']))
        df['Date'] = list(map(datetime.date, df['DateTime']))
        df['Time'] = list(map(datetime.time, df['DateTime']))
        return PostDataFrame(df)

    @classmethod
    def create_from_file(cls, filename):
        ext_indx = filename.find('.')+1
        ext = filename[ext_indx:]
        if 'json' == ext:
            return cls.create_from_json(filename)
        else:
            return cls.create_from_html(filename)

    def clean_empty(self):
        self.df = self.df.fillna('0')
        self.df = self.df.replace('--', '0')

    def create_scaled_counts(self, column):
        data = self.df[column].str.replace(',', '').astype('int')
        data_scaled = data / max(data)
        df = self.df
        df['Scaled ' + column] = data_scaled
        return PostDataFrame(df)

    def create_time_as_seconds(self):
        data = self.df['Time']
        total_seconds_list = []
        for time in data:
            total_seconds = time.hour * 3600 + time.minute * 60 + time.second
            total_seconds_list.append(total_seconds)

        df = self.df
        df['Time in seconds'] = total_seconds_list
        return PostDataFrame(df)

    def create_scaled_time(self):
        pdf = self.create_time_as_seconds()

        total_seconds_list = pdf.df['Time in seconds']
        avg_total_secs = sum(total_seconds_list) / len(total_seconds_list)

        diff_time = [secs - avg_total_secs for secs in total_seconds_list]
        abs_diff_time = [abs(dsecs) for dsecs in diff_time]
        max_abs_diff = max(abs_diff_time)
        scaled_time = [dsecs / (2 * max_abs_diff) for dsecs in diff_time]
        scaled_time = [st + 0.5 for st in scaled_time]

        pdf.df['Scaled Time'] = scaled_time
        return pdf

    def create_scaled_count_data(self):
        pdf = self.create_scaled_counts('Likes')
        pdf = pdf.create_scaled_counts('Likes')
        pdf = pdf.create_scaled_counts('Accounts reached')
        pdf = pdf.create_scaled_counts('Shares')
        pdf = pdf.create_scaled_counts('Follows')
        return pdf

    def plot_dates_vs_scaled_date(self):
        pdf = PostDataFrame(self.df.sort_values(by=['DateTime']))
        orig_columns = pdf.df.columns
        pdf = pdf.create_scaled_count_data()
        pdf = pdf.create_scaled_time()
        df = pdf.df.melt(id_vars=orig_columns,
                         value_vars=['Scaled Likes',
                                     'Scaled Accounts reached',
                                     'Scaled Shares',
                                     'Scaled Follows',
                                     'Scaled Time'])

        pdf_fig = px.scatter(df,
                             x='Date',
                             y='value',
                             color='variable',
                             hover_name='variable',
                             hover_data={'value': False,
                                         'variable': False,
                                         'Date': True,
                                         'Time': True,
                                         'Likes': True,
                                         'Accounts reached': True,
                                         'Shares': True,
                                         'Follows': True},
                             labels={'variable': ''})

        pdf_fig.show()

    def plot_time_vs_scaled_date(self, b_calc_reg):
        pdf = PostDataFrame(self.df.sort_values(by=['Time']))
        if b_calc_reg:
            pdf = pdf.create_time_as_seconds()
            x_data = 'Time in seconds'
            trendline_type = 'lowess'
        else:
            time_data = pdf.df['Time']
            today = datetime.today()
            x_time_data = []
            for time in time_data:
                x_time = today
                x_time = x_time.replace(hour = time.hour, minute = time.minute, second = time.second)
                x_time_data.append(x_time)

            pdf.df['X time'] = x_time_data
            x_data = 'X time'
            trendline_type = None

        orig_columns = pdf.df.columns
        pdf = pdf.create_scaled_count_data()

        df = pdf.df.melt(id_vars=orig_columns,
                         value_vars=['Scaled Likes',
                                     'Scaled Accounts reached',
                                     'Scaled Shares',
                                     'Scaled Follows'])

        pdf_fig = px.scatter(df,
                             x=x_data,
                             y='value',
                             color='variable',
                             hover_name='variable',
                             hover_data={'value': False,
                                         'variable': False,
                                         'Date': True,
                                         'Time': True,
                                         'Likes': True,
                                         'Accounts reached': True,
                                         'Shares': True,
                                         'Follows': True},
                             labels={'variable': ''},
                             trendline= trendline_type)

        pdf_fig.show()


# class PostDataFrameJSON:
#     def __init__(self, df):
#         self.df = df
#
#     @classmethod
#     def create_from_json(cls, json_file_str):
#         with open(json_file_str, 'r') as f:
#             data = json.loads(f.read())
#
#         # Normalizing data
#         df = pd.json_normalize(data, 'organic_insights_posts')
#         df.replace('', np.nan, inplace=True)
#         df.dropna(inplace=True, how='all', axis=1) # Remove empty columns
#         df.replace('--', '0', inplace=True)
#         df.replace(np.nan, '0', inplace=True)
#         df.drop(['string_map_data.Profile Visits.timestamp',
#                  'string_map_data.Impressions.timestamp',
#                  'string_map_data.Follows.timestamp',
#                  'string_map_data.Accounts reached.timestamp',
#                  'string_map_data.Saves.timestamp',
#                  'string_map_data.Likes.timestamp',
#                  'string_map_data.Comments.timestamp',
#                  'string_map_data.Shares.timestamp',
#                  'string_map_data.Website taps.timestamp',
#                  'string_map_data.Email button taps.timestamp',
#                  'string_map_data.Product Page Views.timestamp',
#                  'string_map_data.Product Button Clicks.timestamp',
#                  'string_map_data.Creation Timestamp.timestamp'], axis=1, inplace=True)
#         df.rename(columns={'media_map_data.Media Thumbnail.uri': 'Photo Filename',
#                            'media_map_data.Media Thumbnail.creation_timestamp': 'Timestamp',
#                            'media_map_data.Media Thumbnail.media_metadata.photo_metadata.exif_data': 'Photo Data',
#                            'media_map_data.Media Thumbnail.title': 'Post Caption',
#                            'string_map_data.Profile Visits.value': 'Profile Visits',
#                            'string_map_data.Impressions.value': 'Impressions',
#                            'string_map_data.Follows.value': 'Follows',
#                            'string_map_data.Accounts reached.value': 'Accounts Reached',
#                            'string_map_data.Saves.value': 'Saves',
#                            'string_map_data.Likes.value': 'Likes',
#                            'string_map_data.Comments.value': 'Comments',
#                            'string_map_data.Shares.value': 'Shares',
#                            'string_map_data.Website taps.value': 'Website clicks',
#                            'media_map_data.Media Thumbnail.media_metadata.video_metadata.exif_data': 'Video Data',
#                            'string_map_data.Email button taps.value': 'Email clicks',
#                            'media_map_data.Media Thumbnail.product_tags': 'Product Tags',
#                            'string_map_data.Product Page Views.value': 'Product Page Views',
#                            'string_map_data.Product Button Clicks': 'Product Button Clicks'
#                            }, inplace=True)
#         df['DateTime'] = list(map(datetime.fromtimestamp, df['Timestamp']))
#         df['Date'] = list(map(datetime.date, df['DateTime']))
#         df['Time'] = list(map(datetime.time, df['DateTime']))
#         return PostDataFrameJSON(df)
#
#     def create_scaled_counts(self, column):
#         data = self.df[column].str.replace(',', '').astype('int')
#         data_scaled = data / max(data)
#         df = self.df
#         df['Scaled ' + column] = data_scaled
#         return PostDataFrameJSON(df)
#
#     def create_time_as_seconds(self):
#         data = self.df['Time']
#         total_seconds_list = []
#         for time in data:
#             total_seconds = time.hour * 3600 + time.minute * 60 + time.second
#             total_seconds_list.append(total_seconds)
#
#         df = self.df
#         df['Time in seconds'] = total_seconds_list
#         return PostDataFrameHTML(df)
#
#     def create_scaled_time(self):
#         pdf = self.create_time_as_seconds()
#
#         total_seconds_list = pdf.df['Time in seconds']
#         avg_total_secs = sum(total_seconds_list) / len(total_seconds_list)
#
#         diff_time = [secs - avg_total_secs for secs in total_seconds_list]
#         abs_diff_time = [abs(dsecs) for dsecs in diff_time]
#         max_abs_diff = max(abs_diff_time)
#         scaled_time = [dsecs / (2 * max_abs_diff) for dsecs in diff_time]
#         scaled_time = [st + 0.5 for st in scaled_time]
#
#         pdf.df['Scaled Time'] = scaled_time
#         return pdf
#
#     def create_scaled_count_data(self):
#         pdf = self.create_scaled_counts('Likes')
#         pdf = pdf.create_scaled_counts('Likes')
#         pdf = pdf.create_scaled_counts('Accounts reached')
#         pdf = pdf.create_scaled_counts('Shares')
#         pdf = pdf.create_scaled_counts('Follows')
#         return pdf
#
#     def plot_dates_vs_scaled_date(self):
#         pdf = PostDataFrameJSON(self.df.sort_values(by=['DateTime']))
#         orig_columns = pdf.df.columns
#         pdf = pdf.create_scaled_count_data()
#         pdf = pdf.create_scaled_time()
#         df = pdf.df.melt(id_vars=orig_columns,
#                          value_vars=['Scaled Likes',
#                                      'Scaled Accounts Reached',
#                                      'Scaled Shares',
#                                      'Scaled Follows',
#                                      'Scaled Time'])
#
#         pdf_fig = px.scatter(df,
#                              x='Date',
#                              y='value',
#                              color='variable',
#                              hover_name='variable',
#                              hover_data={'value': False,
#                                          'variable': False,
#                                          'Date': True,
#                                          'Time': True,
#                                          'Likes': True,
#                                          'Accounts reached': True,
#                                          'Shares': True,
#                                          'Follows': True},
#                              labels={'variable': ''})
#
#         pdf_fig.show()
#
#     def plot_time_vs_scaled_date(self, b_calc_reg):
#         pdf = PostDataFrameJSON(self.df.sort_values(by=['Time']))
#         if b_calc_reg:
#             pdf = pdf.create_time_as_seconds()
#             x_data = 'Time in seconds'
#             trendline_type = 'lowess'
#         else:
#             time_data = list(pdf.df['Time'].array)
#             today = datetime.today()
#             x_time_data = []
#             for time in time_data:
#                 x_time = today
#                 x_time = x_time.replace(hour = time.hour, minute = time.minute, second = time.second)
#                 x_time_data.append(x_time)
#
#             pdf.df['X time'] = x_time_data
#             x_data = 'X time'
#             trendline_type = None
#
#         orig_columns = pdf.df.columns
#         pdf = pdf.create_scaled_count_data()
#
#         df = pdf.df.melt(id_vars=orig_columns,
#                          value_vars=['Scaled Likes',
#                                      'Scaled Accounts Reached',
#                                      'Scaled Shares',
#                                      'Scaled Follows'])
#
#         pdf_fig = px.scatter(df,
#                              x=x_data,
#                              y='value',
#                              color='variable',
#                              hover_name='variable',
#                              hover_data={'value': False,
#                                          'variable': False,
#                                          'Date': True,
#                                          'Time': True,
#                                          'Likes': True,
#                                          'Accounts Reached': True,
#                                          'Shares': True,
#                                          'Follows': True},
#                              labels={'variable': ''},
#                              trendline= trendline_type)
#
#         pdf_fig.show()


def graph_dates_vs_scaled_data(b_create_from_html):
    if b_create_from_html:
        pdf = PostDataFrameHTML.create_from_html(postInfo_file_html)
        pdf.clean_empty()
        #pdf.plot_dates_vs_scaled_date()
        pdf.plot_time_vs_scaled_date(False)
    else:
        pdf = PostDataFrameJSON.create_from_json(postInfo_file_json)
        pdf.plot_dates_vs_scaled_date()
        pdf.plot_time_vs_scaled_date(False)


def graph_dates_vs_scaled_data2(filename):
    pdf = PostDataFrame.create_from_file(filename)
    pdf.plot_dates_vs_scaled_date()
    pdf.plot_time_vs_scaled_date(False)


# get_followers_not_following(False, 3)
# df_html = PostDataFrameHTML.create_from_html(postInfo_file_html)
# print(df_html)
# df_json = PostDataFrameJSON.create_from_json(postInfo_file_json)
# print(df_json)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    graph_dates_vs_scaled_data2(postInfo_file_html)
    graph_dates_vs_scaled_data2(postInfo_file_json)
    #get_followers_not_following(false)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
