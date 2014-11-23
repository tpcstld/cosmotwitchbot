"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import lib.irc as irc_
from lib.functions_general import *
import lib.functions_commands as commands

class Roboraj:

	def __init__(self, config):
            self.config = config
            self.irc = irc_.irc(config)
            self.socket = self.irc.get_irc_socket_object()
            self.user_list = set()
            self.saved_data = ""


	def run(self):
		irc = self.irc
		sock = self.socket
		config = self.config

                state = 1 # Get initial data
		while True:
                        print "############################################# NEW PACKET ###################################################"
			data = sock.recv(config['socket_buffer_size']).rstrip()

                        data = "".join((self.saved_data, data))
                        self.saved_data = ""

			if len(data) == 0:
				pp('Connection was lost, reconnecting.')
				sock = self.irc.get_irc_socket_object()

			if config['debug']:
				print data

			# check for ping, reply with pong
                        irc.check_for_ping(data)
                        
                        if state == 2:
                            new_data = data.split('\n')
                            for line in new_data[0:-1]:
                                if "End of /NAMES list" in line:
                                    state = 3
                                    print len(self.user_list), "users online"
                                    break
                                header, sep, names = line.partition(" :")
                                self.user_list = self.user_list.union(set(names.split()))

                            if state != 3 and not "End of /NAMES list" in new_data[-1]:
                                self.saved_data = new_data[-1]
                            continue
                        
                        user_list_updated = irc.check_for_user_list_update(data)
                        if user_list_updated:
                            new_data = data.split('\n')
                            for line in new_data:
                                if line:
                                    info = line.split()
                                    if len(info) >= 3:
                                        info[0] = info[0].partition(':')[-1].rpartition('!')[0] 
                                        if info[1] == "JOIN":
                                            self.user_list.add(info[0]) 
                                        if info[1] == "PART":
                                            self.user_list.discard(info[0])
                                    else:
                                        self.saved_data = line
                            if not self.saved_data:
                                if state == 1:
                                    state = 2 #Get current userlist
                                print len(self.user_list), "users online"
                            continue

			if irc.check_for_message(data):
				message_dict = irc.get_message(data)

				channel = message_dict['channel']
				message = message_dict['message']
				username = message_dict['username']

                                print username in self.user_list

				ppi(channel, message, username)

				# check if message is a command with no arguments
				if commands.is_valid_command(message) or commands.is_valid_command(message.split(' ')[0]):
					command = message

					if commands.check_returns_function(command.split(' ')[0]):
						if commands.check_has_correct_args(command, command.split(' ')[0]):
							args = command.split(' ')
							del args[0]

							command = command.split(' ')[0]

							if commands.is_on_cooldown(command, channel):
								pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
									command, username, commands.get_cooldown_remaining(command, channel)), 
									channel
								)
							else:
								pbot('Command is valid and not on cooldown. (%s) (%s)' % (
									command, username), 
									channel
								)
								
								result = commands.pass_to_function(command, args)
								commands.update_last_used(command, channel)

								if result:
									resp = result
									pbot(resp, channel)
									irc.send_message(channel, resp)

					else:
						if commands.is_on_cooldown(command, channel):
							pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
									command, username, commands.get_cooldown_remaining(command, channel)), 
									channel
							)
						elif commands.check_has_return(command):
							pbot('Command is valid and not on cooldown. (%s) (%s)' % (
								command, username), 
								channel
							)
							commands.update_last_used(command, channel)

							resp = '(%s) > %s' % (username, commands.get_return(command))
							commands.update_last_used(command, channel)

							pbot(resp, channel)
							irc.send_message(channel, resp)
