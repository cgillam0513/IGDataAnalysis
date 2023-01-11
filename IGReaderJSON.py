# import requests
# import json
import datetime
from utilies import getGraphConsts, makeApiCall  # , displayApiCallData


class UserIds:
    def __init__(self, page_id: str, instagram_account_id: str, ig_username: str = None):
        self.page_id = page_id
        self.instagram_account_id = instagram_account_id
        self.ig_username = ig_username


class FbApp:
    def __init__(self, name: str, access_token: str, app_id: str, app_secret: str):
        self.name = name
        self.access_token = access_token
        self.app_id = app_id  # Sometimes referred to as client_id
        self.app_secret = app_secret  # Sometimes referred to a client_secret

    def debugAccessToken(self, graph_consts=None, debug='no'):
        """ Get info on an access token

        API Endpoint:
            https://graph.facebook.com/debug_token?input_token={input-token}&access_token={valid-access-token}

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['input_token'] = self.access_token  # input token is the access token
        endpointParams['access_token'] = self.access_token  # access token to get debug info on

        if graph_consts is None:
            graph_consts = getGraphConsts()

        url = graph_consts['graph_domain'] + '/debug_token'  # endpoint url

        response = makeApiCall(url, endpointParams, debug)  # make the api call

        print('\nDebug Access token for: ' + self.name)
        print("\nData Access Expires at: ")  # label
        print(datetime.datetime.fromtimestamp(
            response['json_data']['data']['data_access_expires_at']))  # display out when the token expires

        print("\nToken Expires at: ")  # label
        print(datetime.datetime.fromtimestamp(
            response['json_data']['data']['expires_at']))  # display out when the token expires

        return response

    def getLongLivedAccessToken(self, graph_consts=None):
        # This does not always work and has not been fully tested!!
        """ Get long lived access token

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={your-access-token}

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['grant_type'] = 'fb_exchange_token'  # tell facebook we want to exchange token
        endpointParams['client_id'] = self.app_id  # client id from facebook app
        endpointParams['client_secret'] = self.app_secret  # client secret from facebook app
        endpointParams['fb_exchange_token'] = self.access_token  # access token to get exchange for a long lived token
        # endpointParams['redirect_uri'] = params['redirect_uri']

        if graph_consts is None:
            graph_consts = getGraphConsts()

        url = graph_consts['endpoint_base'] + 'oauth/access_token'  # endpoint url

        response = makeApiCall(url, endpointParams, 'no')  # make the api call

        print("\n ---- ACCESS TOKEN INFO ----\n")  # section header
        print("Access Token:")  # label
        print(response['json_data']['access_token'])  # display access token

    def getMyUserPages(self, graph_consts=None, b_print=False):
        """ Get facebook pages for a user

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/me/accounts?access_token={access-token}

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['access_token'] = self.access_token  # access token

        if graph_consts is None:
            graph_consts = getGraphConsts()
        url = graph_consts['endpoint_base'] + 'me/accounts'  # endpoint url

        response = makeApiCall(url, endpointParams, 'no')  # make the api call

        return response

    def getInstagramBusinessAccount(self, page_id, graph_consts=None, b_print=False):
        """ Get instagram account

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/{page-id}?access_token={your-access-token}&fields=instagram_business_account

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['access_token'] = self.access_token  # tell facebook we want to exchange token
        endpointParams['fields'] = 'instagram_business_account'  # access token

        if graph_consts is None:
            graph_consts = getGraphConsts()
        url = graph_consts['endpoint_base'] + page_id  # endpoint url

        response = makeApiCall(url, endpointParams, 'no')  # make the api call

        json_data = response['json_data']
        new_page_id = json_data['id']
        if new_page_id != page_id:
            print("\nOld and new page id's do not match!\n")

        if 'instagram_business_account' in json_data:
            ig_business_accnt_id = json_data['instagram_business_account']['id']
        else:
            ig_business_accnt_id = None

        if b_print:
            print("Instagram Business Account Id:  " + str(ig_business_accnt_id))  # display the instagram account id

        return ig_business_accnt_id

    def getMyInstagramBusinessAccount(self, graph_consts=None, b_print=False):
        """ Get instagram account

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/{page-id}?access_token={your-access-token}&fields=instagram_business_account

        Returns:
            object: data from the endpoint

        """

        user_pages = self.getMyUserPages(graph_consts, True)

        user_pages_data = user_pages['json_data']['data']
        for data in user_pages_data:
            page_id = data['id']
            if b_print:
                print(data['name'])
            ig_business_accnt_id = self.getInstagramBusinessAccount(page_id, graph_consts, b_print)
            if ig_business_accnt_id is None:
                print()
            else:
                break

        return ig_business_accnt_id, page_id

    def getAccountInfo(self, user_ids: UserIds, graph_consts=None, b_print=False):
        """ Get info on a users account

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['fields'] = 'business_discovery.username(' + user_ids.ig_username \
                                   + '){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,' \
                                     'followers_count,media_count}'  # string of fields to get back with the request for the account
        endpointParams['access_token'] = self.access_token  # access token

        if graph_consts is None:
            graph_consts = getGraphConsts()
        url = graph_consts['endpoint_base'] + user_ids.instagram_account_id  # endpoint url

        response = makeApiCall(url, endpointParams, 'no')  # make the api call

        if b_print:
            print("\n---- ACCOUNT INFO -----\n")  # display latest post info
            print("username:")  # label
            print(response['json_data']['business_discovery']['username'])  # display username
            # print( "\nwebsite:" ) # label
            # print(response['json_data']['business_discovery']['website'])  # display users website
            print("\nnumber of posts:")  # label
            print(response['json_data']['business_discovery']['media_count'])  # display number of posts user has made
            print("\nfollowers:")  # label
            print(response['json_data']['business_discovery'][
                      'followers_count'])  # display number of followers the user has
            print("\nfollowing:")  # label
            print(response['json_data']['business_discovery'][
                      'follows_count'])  # display number of people the user follows
            print("\nprofile picture url:")  # label
            print(response['json_data']['business_discovery']['profile_picture_url'])  # display profile picutre url
            # print("\nbiography:" ) # label
            # print(response['json_data']['business_discovery']['biography'])  # display users about section
        return response

    def getMyAccountInfo(self, my_user_ids: UserIds = None, graph_consts=None, b_print=False):
        """ Get info on a users account

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

        Returns:
            object: data from the endpoint

        """
        if my_user_ids is None:
            my_user_ids = MyUserId.createMyUserId(self, graph_consts)

        return self.getAccountInfo(my_user_ids, graph_consts, b_print)

    def getUserMedia(self, user_ids: UserIds, pagingUrl='', graph_consts=None, b_print=False):
        """ Get users media

        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/{ig-user-id}/media?fields={fields}&access_token={access-token}

        Returns:
            object: data from the endpoint

        """

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams[
            'fields'] = 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username'  # fields to get back
        endpointParams['access_token'] = self.access_token  # access token

        if graph_consts is None:
            graph_consts = getGraphConsts()

        if '' == pagingUrl:  # get first page
            url = graph_consts['endpoint_base'] + user_ids.instagram_account_id + '/media'  # endpoint url
        else:  # get specific page
            url = pagingUrl  # endpoint url

        response = makeApiCall(url, endpointParams, 'no')  # make the api call

        if b_print:
            print("\n\n\n\t\t\t >>>>>>>>>>>>>>>>>>>> PAGE 1 <<<<<<<<<<<<<<<<<<<<\n")  # display page 1 of the posts

            for post in response['json_data']['data']:
                print("\n\n---------- POST ----------\n")  # post heading
                print("Link to post:")  # label
                print(post['permalink'])  # link to post
                print("\nPost caption:")  # label
                print(post['caption'])  # post caption
                print("\nMedia type:")  # label
                print(post['media_type'])  # type of media
                print("\nPosted at:")  # label
                print(post['timestamp'])  # when it was posted

            # response = self.getUserMedia(user_ids, graph_consts,
            #                              response['json_data']['paging']['next'])  # get next page of posts from the api
            #
            # print("\n\n\n\t\t\t >>>>>>>>>>>>>>>>>>>> PAGE 2 <<<<<<<<<<<<<<<<<<<<\n")  # display page 2 of the posts
            #
            # for post in response['json_data']['data']:
            #     print("\n\n---------- POST ----------\n")  # post heading
            #     print("Link to post:")  # label
            #     print(post['permalink'])  # link to post
            #     print("\nPost caption:")  # label
            #     print(post['caption'])  # post caption
            #     print("\nMedia type:")  # label
            #     print(post['media_type'])  # type of media
            #     print("\nPosted at:")  # label
            #     print(post['timestamp'])  # when it was posted

    def getMyUserMedia(self, my_user_ids: UserIds = None, pagingUrl='', graph_consts=None, b_print=False):
        if my_user_ids is None:
            my_user_ids = MyUserId.createMyUserId(self, graph_consts=graph_consts)

        return self.getUserMedia(my_user_ids, pagingUrl, graph_consts, b_print)

    def getMyFields(self, my_user_ids: UserIds = None, graph_consts = None):#, b_print=False):
        if graph_consts is None:
            graph_consts = getGraphConsts()

        if my_user_ids is None:
            my_user_ids = MyUserId.createMyUserId(self, graph_consts)

        endpointParams = dict()  # parameter to send to the endpoint
        endpointParams['access_token'] = self.access_token  # access token
        url = graph_consts['endpoint_base'] + my_user_ids.instagram_account_id # endpoint url
        return makeApiCall(url, endpointParams, 'yes')  # make the api call


class MyUserId(UserIds):
    @classmethod
    def createMyUserId(cls, fb_app: FbApp, graph_consts=None):
        if graph_consts is None:
            graph_consts = getGraphConsts()

        ig_id, page_id = fb_app.getMyInstagramBusinessAccount(graph_consts)
        return UserIds(page_id, ig_id, 'more_ig_insights')


class GraphCaller:
    def __init__(self, fb_app: FbApp, user_ids: UserIds):
        self.graph_consts = getGraphConsts()
        self.fbApp = fb_app
        self.userIds = user_ids

    def debugAccessToken(self):
        return self.fbApp.debugAccessToken(self.graph_consts)

    def getLongLivedAccessToken(self):
        return self.fbApp.getLongLivedAccessToken(self.graph_consts)

    # def getMyUserPages(self):
    #     my_user_ids = self.userIds


getStarted_app = FbApp('GetStarted',
                       'EAAQBZBK60IXsBAK0HgP10OmvMZCuJgicZBdnZBmgTwrmQvAcJiN2Jrg02bgDpmZBucInqHiZADDnxMGCcZB1d1CwZAabfB68xEwUgxQFwqQZBBz25yZBFWlqZBXTVZCdXqrvnXpw9SptVRmsggELCuxEAmfk5mXlYp0DKiaZCQEomxiYgRgZDZD',
                       '593120055695582',
                       'f1eaeeb1a48aaa00c709cd16fdaf6751')

influencersGraphs_app = FbApp('Influencer Graphs',
                              'EAAI8GpzbiZAMBAEZCqyyn7eCZCl7Lzk0xslYi1QkqZAZCDM3mZAq6g4SeIWOOTPRdnN9hqG37eV6kZBZBxHhkGvxThsAPM6VZBzuDJB78ZCZARSASYmyLoXSqkZB9Ma3wznMxlZCQBNmdXDzOnLenoESJfGFdoinueUM6mmy8EA2I8NZB3KwZDZD',
                              '629034951870867',
                              '9bfd2d3d8bf7439f7c31fa48d7d82dd0')

#influencersGraphs_app.debugAccessToken(debug = 'yes')
response = influencersGraphs_app.getMyFields()
print(response)
