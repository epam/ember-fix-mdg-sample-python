# Sample Market Data client using QuickFIX

This sample shows how to receive FIX Market Data using popular QuickFIX Python library

## **Pre-requisites**

* Install Python 3.7+ and pip:

```sh
sudo yum install python3-devel python3-wheel  
```
  
* Install [QuickFIX](https://pypi.org/project/quickfix/) Python library using pip command:  
  
```sh
pip3 install quickfix  
```
  
* Setup Deltix FIX Gateway.
* Download this sample files to your work directory.

## **Configure**

Modify config/sample_md_client.cfg according to your Ember configuration as follows:

* Point SocketConnectHost and SocketConnectPort to your Deltix FIX Gateway,
* Make sure SenderCompID, TargetCompID match the FIX Session you want to connect as.
* I password is required modify user name and password in fix_session.py
* Update FileStorePath and FileLogPath if necessary.

## **Run**

To run the sample client, execute sample_md_client.py with sample_md_client.cfg as a parameter on Python 3.x:

```sh
python3 src/sample_md_client.py config/sample_md_client.cfg
```

If client is able to connect, it will show a message about successful login and then start printing market data snapshot messages.

