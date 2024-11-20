from utils import CortexV2
from utils import mental_command_train
import json
from utils.cortexV2 import CortexV2
from utils.mental_command_train import TrainV2


# Please fill your application clientId and clientSecret before running script
your_app_client_id = 'xGLKsWuCpPVqQCd9bKMBD1C2vE2GXg29iGOdR14s'
your_app_client_secret = 'QLK3TEGlfO2BDYmOw8HpUVAEzuZDBbw3LAoCDFURMbDl7udwMkGRMywG9COaUzPnSNopKw0ZYbvC22ZukO1h4FpOufnu3m5p7Prg97pKY2kjj9fsgZdRboyZdOG3XvwX'

# Init Train
t=TrainV2(your_app_client_id, your_app_client_secret)
#
profile_name = 'testprof' # set your profile name. If the profile is not exited it will be created.
#
# # list actions which you want to train
actions = ['neutral', 'push', 'pull']
t.start(profile_name, actions)


