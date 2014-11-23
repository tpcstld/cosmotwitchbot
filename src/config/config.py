global config

config = {
	
	# details required to login to twitch IRC server
	'server': 'irc.twitch.tv',
	'port': 6667,
	'username': 'tpcstld',
	'oauth_password': 'oauth:', # get this from http://twitchapps.com/tmi/

	# if set to true will display any data received
	'debug': False,
	
	# channel to join
	'channels': ['#cosmowright'],

	'cron': {
                '#tpcstld': {
                    'run_cron': False,
                    'run_time': '1',
                    'cron_messages': [
                        'This is a test.'
                    ]
                }
	},

	# if set to true will log all messages from all channels
	# todo
	'log_messages': True,

	# maximum amount of bytes to receive from socket - 1024-4096 recommended
	'socket_buffer_size': 2048
}

