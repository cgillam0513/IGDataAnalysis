from abc import ABC
from html.parser import HTMLParser
from datetime import datetime
import pandas as pd
import plotly.express as px


followers_file = "/Users/christophergillam/Downloads/squarelightjeep_20220730/followers_and_following/followers.html"
following_file = "/Users/christophergillam/Downloads/squarelightjeep_20220730/followers_and_following/following.html"
postInfo_file = "/Users/christophergillam/Downloads/squarelightjeep_20220730/past_instagram_insights/posts.html"


def get_followers_not_following():
    def get_user_names(file_str):
        f = open(file_str, "r")
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

        return un_list

    followers_list = get_user_names(followers_file)
    following_list = get_user_names(following_file)
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
            return PostDataFrame(parser.df)

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

    def plot_time_vs_scaled_date(self):
        pdf = PostDataFrame(self.df.sort_values(by=['Time']))
        pdf = pdf.create_time_as_seconds()
        orig_columns = pdf.df.columns
        pdf = pdf.create_scaled_count_data()

        df = pdf.df.melt(id_vars=orig_columns,
                         value_vars=['Scaled Likes',
                                     'Scaled Accounts reached',
                                     'Scaled Shares',
                                     'Scaled Follows'])

        pdf_fig = px.scatter(df,
                             x='Time in seconds',
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
                             trendline= 'lowess')

        pdf_fig.show()


def graph_dates_vs_scaled_data():
    pdf = PostDataFrame.create_from_html(postInfo_file)
    pdf.clean_empty()
    pdf.plot_dates_vs_scaled_date()
    pdf.plot_time_vs_scaled_date()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    graph_dates_vs_scaled_data()
    get_followers_not_following()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
