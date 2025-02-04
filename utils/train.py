import queue

from utils.cortex import Cortex
from PyQt5.QtCore import pyqtSignal, QObject

class Train(QObject):
    """
    A class to use BCI API to control the training of the mental command detections.

    Attributes
    ----------
    c : Cortex
        Cortex communicate with Emotiv Cortex Service

    Methods
    -------
    do_prepare_steps():
        Do prepare steps before training.
    subscribe_data():
        To subscribe to one or more data streams.
    load_profile(profile_name):
        To load an existed profile or create new profile for training
    unload_profile(profile_name):
        To unload an existed profile or create new profile for training
    train_mc(profile_name, training_action, number_of_train):
        To control the training of the mental command action.
    live(profile_name):
        Load a trained profiles then subscribe mental command data to enter live mode
    on_new_data(*args, **kwargs):
        To handle mental command data emitted from Cortex
    """

    accept_signal = pyqtSignal(str, str)
    reject_signal = pyqtSignal(str, str)
    delete_signal = pyqtSignal(str, str)

    def __init__(self,user):
        """
        Constructs cortex client and bind a function to handle subscribed data streams for the Train object
        If you do not want to log request and response message , set debug_mode = False. The default is True
        """
        self.c = Cortex(user, debug_mode=False)
        self.c.bind(new_com_data=self.on_new_data)
        super().__init__()


    def do_prepare_steps(self):
        """
        Do prepare steps before training.
        Step 1: Connect a headset. For simplicity, the first headset in the list will be connected in the example.
                If you use EPOC Flex headset, you should connect the headset with a proper mappings via EMOTIV Launcher first 
        Step 2: requestAccess: Request user approval for the current application for first time.
                       You need to open EMOTIV Launcher to approve the access
        Step 3: authorize: to generate a Cortex access token which is required parameter of many APIs
        Step 4: Create a working session with the connected headset
        Returns
        -------
        None
        """
        self.c.do_prepare_steps()

    def subscribe_data(self, streams):
        """
        To subscribe to one or more data streams
        'com': Mental command
        'fac' : Facial expression

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['com']

        Returns
        -------
        None
        """
        self.c.sub_request(streams)

    def load_profile(self, profile_name):
        """
        To load an existed profile or create new profile for training

        Parameters
        ----------
        profile_name : str, required
            profile name

        Returns
        -------
        None
        """
        profiles = self.c.query_profile()

        if profile_name not in profiles:
            status = 'create'
            self.c.setup_profile(profile_name, status)

        status = 'load'
        self.c.setup_profile(profile_name, status)

    def unload_profile(self, profile_name):
        """
        To unload an existed profile or create new profile for training

        Parameters
        ----------
        profile_name : str, required
            profile name

        Returns
        -------
        None
        """
        profiles = self.c.query_profile()

        if profile_name in profiles:
            status = 'unload'
            self.c.setup_profile(profile_name, status)
        else:
            print("The profile " + profile_name + " is not existed.")

    def train_mc(self, training_action, q_train):
        print('begin train -----------------------------------')
        status = 'start'
        self.c.train_request(detection='mentalCommand',
                             action=training_action,
                             status=status,
                             q=q_train)

    def accept_training(self, profile_name, training_action):
        q_accept = queue.Queue()
        status = 'accept'
        self.c.train_request(detection='mentalCommand',
                             action=training_action,
                             status=status,
                             q=q_accept)
        status = "save"
        self.c.setup_profile(profile_name, status)
        print('save successful')

    def delete_training(self, profile_name, training_action):
        q_delete = queue.Queue()
        status = 'erase'
        self.c.train_request(detection='mentalCommand',
                             action=training_action,
                             status=status,
                             q=q_delete)
        status = "save"
        self.c.setup_profile(profile_name, status)
        print('save successful')

    def reject_training(self, profile_name, training_action):
        q_reject = queue.Queue()
        status = 'reject'

        self.c.train_request(detection='mentalCommand',
                             action=training_action,
                             status=status,
                             q=q_reject)
        status = "save"
        self.c.setup_profile(profile_name, status)
        print('save successful')

    def live(self, profile_name, threshold, delay, key):
        """
        Load a trained profiles then subscribe mental command data to enter live mode

        Returns
        -------
        None
        """
        print('begin live mode ----------------------------------')
        # load profile
        status = 'load'
        # self.c.setup_profile(profile_name, status)


        # sub 'com' stream and view live mode
        stream = ['com']

        self.c.sub_request_GRH(stream, threshold, delay, key)

    def get_trained_data(self, profile_name):
        temp = self.c.get_training_data(profile_name)
        return temp['result']['trainedActions']

    def get_brain_map_data(self, profile_name):
        brainMap = self.c.brain_map(profile_name)
        return brainMap

    def on_new_data(self, *args, **kwargs):
        """
        To handle mental command data emitted from Cortex

        Returns
        -------
        data: dictionary
             the format such as {'action': 'neutral', 'power': 0.0, 'time': 1590736942.8479}
        """
        data = kwargs.get('data')
        print('mc data: {}'.format(data))


# -----------------------------------------------------------




import threading
def train_MC_thread(user,profile,mc):
    t = Train(user)
    t.do_prepare_steps()
    t.subscribe_data(['sys'])
    t.load_profile(profile)
    t.train_mc(profile, mc)
    t.unload_profile(profile)

def create_profile(user,ProfileName):
    t = Train(user)
    t.do_prepare_steps()
    t.subscribe_data(['sys'])
    t.load_profile(ProfileName)
    if t.get_trained_data(ProfileName):
        t.unload_profile(ProfileName)
        return t.get_trained_data(ProfileName)
    t.unload_profile(ProfileName)


def train_MC(user,profile,mc):
    # thread = threading.Thread(target=train_MC_thread, args=(user,profile,mc))
    # thread.start()
    t = Train(user)
    t.do_prepare_steps()
    t.subscribe_data(['sys'])
    t.load_profile(profile)
    t.train_mc(profile, mc)
    # t.unload_profile(profile)



def brain_map(user, profile_name):
    t = Train(user)
    t.do_prepare_steps()
    t.subscribe_data(['sys'])
    t.load_profile(profile_name)
    map_data = t.get_brain_map_data(profile_name)
    print(map_data['result'])
    return map_data['result']

