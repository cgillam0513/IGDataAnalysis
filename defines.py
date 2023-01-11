import requests
import json

def getCreds(app = 'Influencer Graphs') :
	""" Get creds required for use in the applications
	
	Returns:
		dictonary: credentials needed globally

	"""

	creds = dict()  # dictionary to hold everything

	creds['graph_domain'] = 'https://graph.facebook.com/'  # base domain for api calls
	creds['graph_version'] = 'v15.0'  # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds[
		'graph_version'] + '/'  # base endpoint with domain and version
	creds['debug'] = 'no'  # debug mode for api call

	if 'GetStarted' == app:

		creds['access_token'] = 'EAAQBZBK60IXsBAK0HgP10OmvMZCuJgicZBdnZBmgTwrmQvAcJiN2Jrg02bgDpmZBucInqHiZADDnxMGCcZB1d1CwZAabfB68xEwUgxQFwqQZBBz25yZBFWlqZBXTVZCdXqrvnXpw9SptVRmsggELCuxEAmfk5mXlYp0DKiaZCQEomxiYgRgZDZD' # access token for use with all api calls
		creds['client_id'] = '593120055695582' # client id from facebook app IG Graph API Test
		creds['client_secret'] = 'f1eaeeb1a48aaa00c709cd16fdaf6751' # client secret from facebook app

		creds['page_id'] = '100141416168356' # users page id
		creds['instagram_account_id'] = 'INSTAGRAM-BUSINESS-ACCOUNT-ID' # users instagram account id
		creds['ig_username'] = 'IG-USERNAME' # ig username
		creds['redirect_uri'] = 'https://moreinsights.herokuapp.com/auth'

	elif 'Influencer Graphs' == app:
		creds[
			'access_token'] = 'EAAI8GpzbiZAMBAEZCqyyn7eCZCl7Lzk0xslYi1QkqZAZCDM3mZAq6g4SeIWOOTPRdnN9hqG37eV6kZBZBxHhkGvxThsAPM6VZBzuDJB78ZCZARSASYmyLoXSqkZB9Ma3wznMxlZCQBNmdXDzOnLenoESJfGFdoinueUM6mmy8EA2I8NZB3KwZDZD'  # access token for use with all api calls
		creds['client_id'] = '629034951870867'  # client id from facebook app IG Graph API Test
		creds['client_secret'] = '9bfd2d3d8bf7439f7c31fa48d7d82dd0'  # client secret from facebook app
		creds['page_id'] = '100141416168356'  # users page id
		creds['instagram_account_id'] = 'INSTAGRAM-BUSINESS-ACCOUNT-ID'  # users instagram account id
		creds['ig_username'] = 'more_ig_insights'  # ig username
		creds['redirect_uri'] = 'https://moreinsights.herokuapp.com/auth'

	return creds

def makeApiCall( url, endpointParams, debug = 'no' ) :
	""" Request data from endpoint with params
	
	Args:
		url: string of the url endpoint to make request from
		endpointParams: dictionary keyed by the names of the url parameters


	Returns:
		object: data from the endpoint

	"""

	data = requests.get( url, endpointParams ) # make get request

	response = dict() # hold response info
	response['url'] = url # url we are hitting
	response['endpoint_params'] = endpointParams #parameters for the endpoint
	response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
	response['json_data'] = json.loads( data.content ) # response data from the api
	response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

	if ( 'yes' == debug ) : # display out response info
		displayApiCallData( response ) # display response

	return response # get and return content

def displayApiCallData( response ) :
	""" Print out to cli response from api call """

	print("\nURL: " )# title
	print(response['url'] )# display url hit
	print("\nEndpoint Params: ") # title
	print(response['endpoint_params_pretty']) # display params passed to the endpoint
	print("\nResponse: ") # title
	print(response['json_data_pretty']) # make look pretty for cli