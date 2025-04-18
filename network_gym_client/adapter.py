#Copyright(C) 2025 Network Simulation Solutions LLC
#SPDX-License-Identifier: Apache-2.0
#File : adapter.py

import sys
import wandb
import numpy as np
import pandas as pd
import json
import time

from threading import Thread
from rich.live import Live
from rich.layout import Layout

from rich.ansi import AnsiDecoder
from rich.console import Group
from rich.jupyter import JupyterMixin
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn

import plotext as plt

class Adapter:
    """The base class for environment data format adapter.

    This class is an data format "adapter" between the gymnasium environment and network_gym environment.
    It transforms the network stats measurements (json) to obs and reward (Spaces).
    It also transforms the action (Spaces) to a policy (json) that can be applied to the network.
    """
    def __init__(self, config_json):
        """Initialize Adapter.
        
        Args:
            config_json (json): the configuration file
        """
        self.config_json = None
        self.wandb_log_buffer = None
        self.wandb = wandb
        self.config_json = config_json
        self.action_data_format = None

        rl_alg = config_json['rl_config']['agent'] 

        config = {
            "policy_type": "MlpPolicy",
            "env_id": "network_gym_client",
            "RL_algo" : rl_alg
        }
        if config_json["enable_wandb"]:
            self.wandb.init(
                name=config_json['env_config']['env'] + "::" + rl_alg,
                project="network_gym_client",
                config=config,
                sync_tensorboard=True,  # auto-upload sb3's tensorboard metrics
                # save_code=True,  # optional
            )

    def initial_rich_thread(self):
        self.layout = None
        if self.config_json["enable_terminal_redering"]:
            rich_thread = Thread(target=self.rich_live)
            rich_thread.daemon = True  # Dies when main thread (only non-daemon thread) exits.
            rich_thread.start()
    
    def wandb_log_buffer_append (self, info):
        """Add to wandb log buffer, the info will be send to wandb later in the :meth:`wandb_log` function

        Args:
            info (dict): information to append to the buffer.
        """
        if info:
            # info not empty!
            if not self.wandb_log_buffer:
                self.wandb_log_buffer = info
            else:
                self.wandb_log_buffer.update(info)

    def wandb_log (self):
        """Send the log information to WanDB.
        """
        # send info to wandb
        #print(self.wandb_log_buffer)
        if self.config_json["enable_wandb"]:
            self.wandb.log(self.wandb_log_buffer)
        self.wandb_log_buffer = None

    def df_to_dict(self, df, id_name='id'):
        """Transform datatype from pandas.dataframe to dictionary.

        Args:
            df (pandas.dataframe): a pandas.dataframe object
            description (string): a descritption for the data

        Returns:
            dict : converted data with dictionary format
        """
        if df is None:
            return {}
        description = df['source'] + "::" + df['name']
        get_key = lambda u: description+"::"+id_name+f'={u}'
        dict_key = list(map(get_key, df['id']))
        dict_value = df['value']

        #print(dict_key)
        #print(dict_value)

        data = dict(zip(dict_key, dict_value))
        #print(data)
        return data

    def fill_empty_feature(self, feature, value):
        """Fill the  missing measurements with a input value

        Args:
            feature (pd.DataFrame): feature from the measurement
            value (int): the value to fill the missing measurement

        Returns:
            list: results after replace missing measurements with value
        """
        
        #Fill the missing data with the input value.
        
        if feature is None:
            print("[WARNING] all users of a feature returns empty measurement.")
            emptyFeatureArray = np.empty([self.config_json['env_config']['num_users'],], dtype=int)
            emptyFeatureArray.fill(value)
            return emptyFeatureArray

        if len(feature['user']) > self.config_json['env_config']['num_users']:
            print ("[WARNING] This feature has more user than input!!")
            print (feature)
            emptyFeatureArray = np.empty([self.config_json['env_config']['num_users'],], dtype=int)
            emptyFeatureArray.fill(value)
            return emptyFeatureArray
        elif len(feature['user']) == self.config_json['env_config']['num_users']:
            # measurement size match the user number
            return feature["value"]
        elif len(feature['user'])> 0:
            # some of the user's data are missing, fill with input value.
            print("[WARNING] some users of a feature returns empty measurement.")
            #feature = feature.set_index("user")
            #feature = feature.reindex(list(range(self.config_json['env_config']['num_users'])),fill_value=value)
            #data = feature[:]["value"]

            data = np.empty([self.config_json['env_config']['num_users'],], dtype=int)
            data.fill(value)

            for index, user_id in enumerate(feature['user']):
                data[user_id] = feature['value'][index]
            #print(data)
            return data
        else:
            # all user's data are missing, fill the entire feature will input value.
            print("[WARNING] all users of a feature returns empty measurement.")
            emptyFeatureArray = np.empty([self.config_json['env_config']['num_users'],], dtype=int)
            emptyFeatureArray.fill(value)
            return emptyFeatureArray

    def rich_live(self):
        self.layout = self.make_layout()
        header = self.layout['header']
        title = plt.colorize(self.config_json['rl_config']['agent'], "cyan+", "bold" ) + " agent is interacting with NetworkGym's " + plt.colorize(self.config_json['env_config']['env'], "cyan+", "bold") + " env."
        header.update(Text(title, justify = "left"))

        overall_progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TextColumn("env time: {task.completed}/{task.total} ms"),
        )
        overall_task = overall_progress.add_task("Progress", total=self.config_json['env_config']['env_end_time_ms'])

        footer = self.layout["footer"]
        footer.update(overall_progress)
        
        self.layout["main"].visible=False
        step_length = self.config_json['env_config']['measurement_interval_ms']
        if 'measurement_guard_interval_ms' in self.config_json['env_config']:
            step_length = step_length + self.config_json['env_config']['measurement_guard_interval_ms']

        with Live(self.layout, refresh_per_second=1, redirect_stderr=False) as live:
            while True:
                time.sleep(1)
                if self.action_data_format is not None:
                    overall_progress.update(overall_task, completed=self.action_data_format["ts"]+step_length)
                #live.refresh()

    def make_layout(self):
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=1),
            Layout(name="main", ratio=1),
            Layout(name="footer", size = 1),
        )
        layout["main"].split_row(
            Layout(name="left", ratio = 1),
            Layout(name="right", ratio = 1),
        )
        return layout

    class plotextMixin(JupyterMixin):
        def __init__(self, plot_function):
            self.decoder = AnsiDecoder()
            self.plot_function = plot_function

        def __rich_console__(self, console, options):
            self.width = options.max_width or console.width
            self.height = options.height or console.height
            canvas = self.plot_function(self.width, self.height)
            self.rich_canvas = Group(*self.decoder.decode(canvas))
            yield self.rich_canvas
