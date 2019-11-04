
'''
 sslcompare.py : compare ciphers suite to baselines
 Author        : Arthur Le Corguille - William Gougam
'''
from __future__ import print_function
import json
import os
import sys, getopt
import subprocess
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BASELINE = os.path.join(CURRENT_DIR,"baselines","anssi.json")
TESTSSL_PATH = os.path.join(CURRENT_DIR,"testssl.sh","testssl.sh")

color_map = {'green':'\033[92m','yellow':'\033[93m','red':'\033[91m','blue':'\033[94m',
             'magenta':'\033[95m'} 
PROTOCOLS = ["TLS 1", "TLS 1.1", "TLS 1.2","TLS 1.3"]

def print_color(text,color):
    print(color_map[color] + text + '\033[0m')



# Parse testssl.sh output
def get_testssl_output(url):
    p1 = subprocess.Popen([TESTSSL_PATH,'-E',url], stdout=subprocess.PIPE)
    output = (p1.communicate()[0]).split('\n')
    cipher_suites = {}
    protocols = ["TLS 1","TLS 1.1","TLS 1.2","TLS 1.3"]
    for protocol in protocols:
        cipher_suites[protocol] = []
        go = False
    for ligne in output:
        if "Done" in ligne :
            break
	if "TLS 1.3" in ligne:
            current_protocol = "TLS 1.3"
            continue        
	if "TLS 1.2" in ligne:
            current_protocol = "TLS 1.2"
            continue
        elif "TLS 1.1" in ligne:
            current_protocol = "TLS 1.1"
            continue
        elif "TLS 1" in ligne:
            go = True
            current_protocol = "TLS 1"
            continue
        if go and ligne:
            suite = ligne.split()[-1]
            cipher_suites[current_protocol].append(suite)
    return cipher_suites

def print_usage():
    print("Usage : test.py sslcompare.py -u <url or ip> -b <baselinefile>\n\n\
    -u : [MANDATORY] url or ip of the target\n\
    -b : baseline file (json format). Default : anssi.json\n\n\
    Examples :\n\n\
    test.py sslcompare.py -u mytargetsite.com \n\
    test.py sslcompare.py -u mytargetsite.com -b mybaseline.json\n\
    ")
    



# Main function
def main(argv):
    baseline = DEFAULT_BASELINE
    url = ''
    try:
        opts, args = getopt.getopt(argv,"u:b",["url=","baseline="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-u", "--host"):
            url = arg
        elif opt in ("-b", "--baseline"):
            baseline = arg
    if url == '':
        print("You must pass an url as argument : python sslcompare.py -u <url or ip>")
        print_usage()
        sys.exit()
    print("RUNNING testssl.sh...")
    target_suites = get_testssl_output(url)
    with open(baseline) as f:
        baseline_suites = json.load(f)
    suite_categories = ['recommended','degraded','last hope','deprecated']
    for protocol in PROTOCOLS:
        print_color(protocol,'blue')
        suites = {}
        for category in suite_categories:
            suites[category] = []
            
        for suite in target_suites[protocol]:
            if suite in baseline_suites[protocol]['recommended']:
                suites['recommended'].append(suite)
            elif suite in baseline_suites[protocol]['degraded']:
                suites['degraded'].append(suite)
            elif suite in baseline_suites[protocol]['last hope']:
                suites['last hope'].append(suite)
            else :
                suites['deprecated'].append(suite)
        # recommended
        for suite in suites['recommended']:
            print(suite,end='')
            print_color(" [RECOMMENDED]",'green')
        # degraded
        for suite in suites['degraded']:
            print(suite,end='')
            print_color(" [DEGRADED]",'yellow')
        # last hope
        for suite in suites['last hope']:
            print(suite,end='')
            print_color(" [LAST HOPE]",'magenta')
        # deprecated
        for suite in suites['deprecated']:
            print(suite,end='')
            print_color(" [DEPRECATED]",'red')
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print("[+] Start time : ",start_time)
    main(sys.argv[1:])
    end_time = datetime.datetime.now()
    print("[+] End time : ",end_time)

