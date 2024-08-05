# NetworkGym

📋 **[NetworkGym Docs Website](https://intellabs.github.io/networkgym)**

📧 **[Contact Us](mailto:netaigym@gmail.com)**

💻 **[Slack](https://join.slack.com/t/networkgym/shared_invite/zt-23c6nvd5s-1l1m5iVtDZj3LcMgVspdNg)**

NetworkGym is an open-source based network simulation software framework consisting of four modules: Client, Server, Environment, and Simulator. Gym is referenced to OpenAI’s Gym library – an API standard for reinforcement learning (https://gymnasium.farama.org/).

## 💡 Overview

This repository provides source code for all four modules: Client (`network_gym_client`), Server (`network_gym_server`), Environment (`network_gym_env`), and Simulator (`network_gym_sim`): 

- network_gym_sim (license: GPLv2): a ns-3.41 (https://www.nsnam.org/) based full-stack multi-access network simulator enhanced with the support of the Generic Multi Access (GMA) protocol (https://github.com/IntelLabs/gma)

- network_gym_server (license: Apachev2): application software based on ZMQ socket APIs (https://zeromq.org/socket-api/) to support info exchange between network_gym_client and network_gym_sim

- network_gym_client (license: Apachev2): application software to configure network simulation, collect synthetic data and traces, and run algorithms to generate commands and control the simulation	

- network_gym_env (license: Apachev2): application software to connect network simulator with network_gym_server	


## ⌛ Installation
1. (Optional) Create a new virtual python environment.
```
python3 -m venv network_venv
source network_venv/bin/activate
```
2. Install Required Libraries.
```
pip3 install -r requirements.txt
```
3. (For ns-3 Environment Only) Build the `network_gym_sim`
- Install ns-3.41. In the root directory, clone the [ns-3.41](https://www.nsnam.org/releases/ns-3-41/) and name it as `network_gym_sim`:
  ```
  git clone -b ns-3.41 https://gitlab.com/nsnam/ns-3-dev.git network_gym_sim
  ```
  After downloading ns-3, install the dependencies and libraries following the [ns-3 prerequisites](https://www.nsnam.org/docs/tutorial/html/getting-started.html#prerequisites). Build the ns-3 with the following commands. You can find more information on building ns-3 [here](https://www.nsnam.org/docs/tutorial/html/getting-started.html#building-ns-3).
  ```
  cd network_gym_sim
  ./ns3 clean
  ./ns3 configure --build-profile=optimized --disable-examples --disable-tests
  ./ns3 build
  ```

- Copy gma and networkgym module files:
  ```
  cp ../network_gym_ns3/scratch/unified-network-slicing.cc scratch/
  cp ../network_gym_ns3/network_gym_sim.py .
  cp -r ../network_gym_ns3/contrib/* contrib/
  ```
- Install the ZeroMQ socket C++ library (required by networkgym module):
  ```
  apt-get install libczmq-dev
  ```
- In the `network_gym_sim/contrib` folder, clone the 5G nr module from [here](https://gitlab.com/cttc-lena/nr/-/tree/5g-lena-v3.0.y?ref_type=heads), using the 5g-lena-v3.0.y branch:
  ```
  cd contrib
  git clone -b 5g-lena-v3.0.y https://gitlab.com/cttc-lena/nr
  ```
- Add C++ Json library. Replace the `network_gym_sim/contrib/networkgym/model/json.hpp` with the [json.hpp](https://github.com/nlohmann/json/blob/develop/single_include/nlohmann/json.hpp):
  ```
  cd networkgym/model/
  rm json.hpp
  wget https://raw.githubusercontent.com/nlohmann/json/develop/single_include/nlohmann/json.hpp
  ```

- Finally, we need to fix a few bugs in the ns-3. The lte module hard coded the IP addresses for the backhaul links. This two files allows we to customize the IP addresses for the backhaul links. 
  ```
  cd ../../../../
  cp network_gym_sim/contrib/modified/no-backhaul-epc-helper.cc network_gym_sim/src/lte/helper/no-backhaul-epc-helper.cc
  cp network_gym_sim/contrib/modified/point-to-point-epc-helper.cc network_gym_sim/src/lte/helper/point-to-point-epc-helper.cc
  ```
- Try to build ns-3 once again to see if there is any errors:
  ```
  cd network_gym_sim
  ./ns3 build
  ```
- (Optional) With the previous steps, the code should be running without any issue. However, we also identified a few more issues related to TCP or BBR and proposed fixes in the modified files located in `network_gym_sim/contrib/modified/` folder. You can also replace the original files with them if needed. Again, this is not required.

## ☕ Quick Start
First, open 3 terminals (or 3 screen sessions), one per component. Make sure all terminals have activated the virtual environment created in the previous step.
### start server
In the first terminal type following command to start the server:
```
python3 start_server.py
```
The expected output is as following:
```
Max instances per client:
{'test': 1, 'admin': 100}
┏━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Worker ┃ Status ┃ Time since Last Seen (seconds) ┃ Environment ┃
┡━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
└────────┴────────┴────────────────────────────────┴─────────────┘
```

### start ns-3 environment
In the second terminal type following command to start the ns-3 based environment:
```
python3 start_env_ns3.py
```
The expected output from the first (**server**) terminal should be updated as following:
```
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Worker      ┃ Status ┃ Time since Last Seen (seconds) ┃ Environment    ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ admin-0-*** │ idle   │ 13.100512027740479             │ ['nqos_split'] │
└─────────────┴────────┴────────────────────────────────┴────────────────┘
```

### start client
In the third terminal, type the following command to start the client:
```
python3 start_client.py
```
A progress bar should be displayed at the third (client) terminal:
```
system_default agent is interacting with NetworkGym's nqos_split env.                     
⠴ Progress ━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   5% 0:04:41 env time: 4600/101100 ms   
```

## 🎨 Start Python Custom Environment
First, open 3 terminals (or 3 screen sessions), one per component. Make sure all terminals have activated the virtual environment created in the previous step.
### start server
In the first terminal type following command to start the server:
```
python3 start_server.py
```

### start Python custom environment
In the second terminal type following command to start a custom environment:
```
python3 start_custom_env.py
```
The expected output from the first (**server**) terminal should be updated as following:
```
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Worker      ┃ Status ┃ Time since Last Seen (seconds) ┃ Environment      ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ admin-0-*** │ idle   │ 13.100512027740479             │ ['admin-custom'] │
└─────────────┴────────┴────────────────────────────────┴──────────────────┘
```

### start client
Change the environment variable in [start_client.py](start_client.py): `env_name = "custom"`. In the third terminal, type the following command to start the client:
```
python3 start_client.py
```
A progress bar should be displayed at the third (client) terminal:
```
system_default agent is interacting with NetworkGym's custom env.                    
⠴ Progress ━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   5% 0:04:41 env time: 4600/101100 ms   
```

### Substituting the Dummy Simulator
Once you’ve successfully established a connection between your client and the custom environment, you’re ready to substitute the [network_gym_env/dummy_sim.py](network_gym_env/dummy_sim.py) with your proprietary simulator or testbed.


## 🔧 Client Configuration
NetworkGym Client includes two configuration files, a common configure file and environement dependent configure file. 

- Update the common configuration parameters in [common_config.json](network_gym_client/common_config.json):

```json
{
  "connect_via_server_ip_and_server_port": false, //set to ture to use the server_ip and server_port to connect to a Intel cloud server (this method requires Intel VPN);
  "server_ip": "gmasim-v01.jf.intel.com", //do not change (for internal users only).
  "server_port": 8092, //set to 8088 to access stable version or 8092 to access dev version.
  "local_fowarded_port": 8092, // the local port that used to forward to the external server.
  "enable_wandb": false, // sending data to wandb database.
  "enable_terminal_redering": true, // render the network in the terminal.
  "session_name": "admin",//This is for connecting to Intel Cloud server. Make sure to change the "session_name" to your assigned session name. Cannot use '-' in the name! Test account is for testing only (shared by every one). Contact us to apply for an account. 
  "session_key": "admin",//This is for connecting to Intel Cloud server. Make sure to change the "session_key" to your assigned keys.
}
```

- Update the environment dependent configuration file, e.g., [network_gym_client/envs/nqos_split/config.json](network_gym_client/envs/nqos_split/config.json).
  - View configuration suggestions for arguments at [NetworkGym Docs Website](https://intellabs.github.io/networkgym/environments/mx_traffic_management/mx_traffic_splitting.html#arguments).


## 📁 Client File Structure

```
📦 NetworkGym
┣ 📜 start_client_demo.py
┗ 📂 network_gym_client
  ┣ 📜 adapter.py (➡️ WanDB)
  ┣ 📜 common_config.json
  ┣ 📜 env.py
  ┣ 📜 northbound_interface.py (➡️ network_gym_server and network_gym_env)
  ┗ 📂 envs
    ┗ 📂 [ENV_NAME]
      ┣ 📜 adapter.py
      ┗ 📜 config.json
```

- Excuting the 📜 start_client_demo.py file will start a new simulation. To change the environment, modify the `env_name` parameter. The 📜 common_config.json is used in all environments. Depends on the selected environments, the 📜 config.json and 📜 adapter.py in the [ENV_NAME] folder will be loaded. The 📜 adapter.py helps preparing observations, rewards and actions for the selected environment.
- The 📜 start_client_demo.py create a NetworkGym environment, which remotely connects to the ns-3 based NetworkGym Simualtor (hosted in vLab machine) using the 📜 northbound_interface. 📜 start_client_demo.py also uses random samples from the action space to interact with the NetworkGym environment. The results are synced to ➡️ WanDB database. We provide the following code snippet from the 📜 start_client_demo.py as an example:

```python
#Copyright(C) 2023 Intel Corporation
#SPDX-License-Identifier: Apache-2.0
#File : start_client_demo.py

from network_gym_client import load_config_file
from network_gym_client import Env as NetworkGymEnv

client_id = 0
env_name = "nqos_split"
config_json = load_config_file(env_name)
config_json["rl_config"]["agent"] = "random"
# Create the environment
env = NetworkGymEnv(client_id, config_json) # make a network env using pass client id and configure file arguements.

num_steps = 1000
obs, info = env.reset()

for step in range(num_steps):

    action = env.action_space.sample()  # agent policy that uses the observation and info
    obs, reward, terminated, truncated, info = env.step(action)

    # If the environment is end, exit
    if terminated:
        break

    # If the epsiode is up (environment still running), then start another one
    if truncated:
        obs, info = env.reset()
```

## 📚 How to reference "NetworkGym"?

Please use the following to reference "NetworkGym" in your paper if it is used to generate data for the paper: 

Menglei Zhang and Jing Zhu, "NetworkGym: Democratizing Network AI via Simulation-as-a-Service", https://github.com/IntelLabs/networkgym 



