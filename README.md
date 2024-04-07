<center><h1>Software Security Guardian</h1></center>

<center>NIS3366 Group 1</center>

<center>Wang Hexi, Shi Xuanyu, Liu Can, Gu Yunming</center>



## 1. Project Overview 

Software Security Guardian integrates functions such as **malware detection**, **traffic monitoring**, **password management**, and **program correctness verifying** to provide users with comprehensive security protection. Through advanced algorithms and models, we can timely detect and remove malicious software, safeguarding users' network communication security. The password management function facilitates users to securely manage various account password information. Additionally, our program correctness detection function helps users improve code quality and stability. 

Software Security Guardian aims to help users cope with increasingly severe network security threats and ensure the security of personal information and data. 



## 2. Environmental Dependencies

#### Development and Testing Platforms 

1. **Operating System:** Windows 
1. **Programming Software:** Visual Studio Code, Pycharm 
1. **Programming Language:** Python 
1. **Python Environment:** Anaconda Python 3.8 
1. **Database:** PostgreSQL 
1. **Testing Environment:** Anaconda shell



#### Running Environment

Database: PostgreSQL

The following are additional dependencies required by the software:

* Python (recommended version is 3.8) 

* PyQt-Fluent-Widgets 

* ember (recommended installation method: pip install git+https://github.com/elastic/ember.git) 

* tqdm 

* numpy (recommended version: 1.23.5)

* pandas 

* lightgbm 

* lief (recommended version: 0.12.1) 

* scikit-learn (recommended version: 0.23.2) 

* z3-solver 

* lark 

* matplotlib 

* scapy 

* Crypto 

* werkzeug 

* captcha 

* psycopg2

  

## 3. Installation Instructions

#### Method 1: Run our Docker **container**

#### Method 2: Local Installation

1. ```
   pip install requirement.txt
   ```

2. Download and install the PostgreSQL database.

3. Configure the database connection information:

   * Open the `utils.py` file and modify the corresponding `hostname`, `databasename`, `username`, `password`, and `port`.



## 4. Running Instructions

1. Start the PostgreSQL database:

   ```
   $ pg_ctl start -D "PostgreSQLdata database address"
   ```

2. Execute the following command in the terminal to launch the application:

   ```
   $ python demo.py
   ```



## 5. Usage Instructions

- Ensure that the PostgreSQL database is correctly configured and running.

- You can use command-line control to facilitate debugging of the database:

  ```
  $ postgres://username:password@host:port/dbname
  ```

- When modifying the database connection information in `utils.py`, please proceed with caution to ensure consistency with the actual configuration.



## 6. Author Information

* https://github.com/halsayxi
* https://github.com/ccliu-u
* https://github.com/Gym1013
* https://github.com/HxppyThxught
