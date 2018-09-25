#### DESCRIPTION
This python script compares tls cipher suites of a server to baselines.

Cipher suites are retrieved with the testssl.sh shell script (https://github.com/drwetter/testssl.sh).


#### GUIDE 
To launch the script :

```sh
 python sslcompare.py -u <url or ip> -b <baselinefile>
   -u : [MANDATORY] url or ip of the target
   -b : baseline file (json format). Default : anssi.json
```
   
Examples :
```sh
   python sslcompare.py -u mytargetsite.com 
   python sslcompare.py -u mytargetsite.com -b mybaseline.json
```
#### Baseline files :

Baseline are formated as json files.

Baseline files are stored in the baseline directory.

Default baseline file is anssi.json (ANSSI recommendations).

For each tsl version suite can be either :
- recommended
- degraded
- last hope (suites that can be used as a last resort)
- depreciated

To add a baseline, create a file and fill it the same way
anssi.json is filled.

Then pass your baseline file in the command line :
```sh
python sslcompare.py -u mytargetsite.com -b mybaseline.json
```

   
#### NOTES 

TLS 1 is equivalent to TLS 1.0
