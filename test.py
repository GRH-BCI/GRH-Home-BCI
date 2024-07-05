# import liesl
# import time
#
# streams = liesl.print_available_streams()  # list of available streams
# desired_stream = liesl.get_streams_matching(name="UnityMarkerStream")  # get specific EEG streams
# # print (desired_stream[0])
# stream = liesl.open_stream(name="UnityMarkerStream")
# stream_dict = liesl.inlet_to_dict(stream)  # convert inlet info to a dictionary object
# # print(stream_dict)
#
# # # to constantly read EEG and save the stream into a ringbuffer
# sinfo = liesl.get_streaminfos_matching(name="UnityMarkerStream")[0]
#
#
# # s_rate = 100  # sampling rate
# # rb = liesl.RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
# # rb.await_running()
# # time.sleep(5)
# # chunk, tstamps = rb.get()
# # assert chunk.shape == [5 * s_rate, 8]  # for 1s of data and 8 channels
#
# # use a session to record data while other tasks are being performed
# def _save_stream_data(self, session_name: str, task_func, *args):
#     streamargs = [{'name': self.stream_name, "hostname": self.local_host_name}]
#     session = liesl.Session(prefix="bessy_stream_data", streamargs=streamargs)
#     with session(session_name):
#         task_func(*args)  #this can be self.main(*args)
#         # the streams are recorded to ~/labrecording/bessy_stream_data/session_name_R001.xdf
#
import spotify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials(client_id='0e423e5c8c0d40539e57f9ae89d27109',
        client_secret='0d6e0656993e45d0bd5283db68516ab4')
import json
import spotipy
import webbrowser
client_id = '0e423e5c8c0d40539e57f9ae89d27109'
client_secret = '0d6e0656993e45d0bd5283db68516ab4'
redirect_uri = 'https://www.imagination-centre.ca/'
scope = "user-read-playback-state,user-modify-playback-state"

sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
          client_id=client_id,
          client_secret=client_secret,
          redirect_uri=redirect_uri,
          scope=scope, open_browser=False))

# Shows playing devices
res = sp.devices()
print(res)

res = sp.devices()

