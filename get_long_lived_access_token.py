from defines import getCreds, makeApiCall
from debug_access_token import debugAccessToken

def getLongLivedAccessToken(params):
    """ Get long lived access token
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={your-access-token}

	Returns:
		object: data from the endpoint

	"""

    endpointParams = dict()  # parameter to send to the endpoint
    endpointParams['grant_type'] = 'fb_exchange_token'  # tell facebook we want to exchange token
    endpointParams['client_id'] = params['client_id']  # client id from facebook app
    endpointParams['client_secret'] = params['client_secret']  # client secret from facebook app
    endpointParams['fb_exchange_token'] = params['access_token']  # access token to get exchange for a long lived token
    #endpointParams['redirect_uri'] = params['redirect_uri']


    url = params['endpoint_base'] + 'oauth/access_token'  # endpoint url

    return makeApiCall(url, endpointParams, params['debug'])  # make the api call


params = getCreds()  # get creds
params['debug'] = 'yes'  # set debug
#debug_access_token(params)
response = getLongLivedAccessToken(params)  # hit the api for some data!

print("\n ---- ACCESS TOKEN INFO ----\n")  # section header
print("Access Token:")  # label
print(response['json_data']['access_token'])  # display access token
