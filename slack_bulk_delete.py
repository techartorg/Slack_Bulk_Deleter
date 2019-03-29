from urllib.parse import urlencode
from urllib.request import urlopen
import time
import json
import codecs
import datetime
from collections import OrderedDict

reader = codecs.getreader( 'utf-8' )

# Obtain here: https://api.slack.com/custom-integrations/legacy-tokens
token = '' # EACH USER MUST PUT IN THEIR OWN TOKEN AND THEN REMOVE IT BEFORE THEY SUBMIT A MODIFIED SCRIPT TO THE REPO

# Set it to delete only this user's files. Handy if you are not admin.
member_id= ''

# Params for file listing. More info here: https://api.slack.com/methods/files.list

# Delete files older than this:
days = 30
ts_to = int( time.time( ) ) - days * 24 * 60 * 60

# How many? ( Maximum is 1000, otherwise it defaults to 100 )
count = 1000

# Types?
#types = 'all'
types = 'videos,images,gdocs,pdfs,zips'
#types = 'zips'
#types = 'videos,images'

def list_files( user = '' ):
	params = { 'token': token,
				  'ts_to': ts_to,
				  'count': count,
				  'types': types,
				  'user': user,
				  }
	uri = 'https://slack.com/api/files.list'
	response = reader( urlopen( uri + '?' + urlencode( params ) ) )
	return json.load( response )[ 'files' ]


def greater_mb( file, mb ):
	return file[ 'size' ] / 1000000 >= mb


def smaller_mb( file, mb ):
	return file[ 'size' ] / 1000000 < mb


def filter_by_size( files, greater_or_smaller, mb ):
	return [ file for file in files if greater_or_smaller( file, mb ) ]

def info( file ):
	order = [ 'Title', 'Name', 'Created', 'Size', 'Filetype', 'Comment', 'Permalink', 'Download', 'User', 'Channels' ]
	info = { 'Title': file[ 'title' ],
				'Name': file[ 'name' ],
				'Created': datetime.datetime.utcfromtimestamp( file[ 'created' ] ).strftime( '%B %d, %Y %H:%M:%S' ),
				'Size': str( file[ 'size' ] / 1000000 ) + ' MB',
				'Filetype': file[ 'filetype' ],
				'Comment': file[ 'initial_comment' ] if 'initial_comment' in file else '',
				'Permalink': file[ 'permalink' ],
				'Download': file[ 'url_private' ],
				'User': file[ 'user' ],
				'Channels': file[ 'channels' ], }

	return OrderedDict( ( key, info[ key ] ) for key in order )


def delete_files( files ):
	num_files = len( files )
	file_ids = map( lambda f: f[ 'id' ], files )
	print( 'Deleting %i files'%num_files )

	uri = 'https://slack.com/api/files.delete'

	for index, file_id in enumerate( file_ids ):
		params = { 'token': token, 'file': file_id }

		response = reader( urlopen( uri + '?' + urlencode( params ) ) )
		print( ( index + 1, 'of', num_files, '-', file_id, json.load( response )[ 'ok' ] ) )
		time.sleep(  1 )

print( 'Retrieving files older than %s days'%( days ) )

files = list_files( member_id )

print( 'Total %i files'%len( files ) )

files = filter_by_size( files, greater_mb, 50 )

print( 'Match size %i files' % len( files ) )

delete_files( files ) # Commented out, so you don't accidentally run this.
