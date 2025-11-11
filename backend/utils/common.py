from datetime import datetime

def processStartMsg(message):
    print("\n______________________________________________________________________")
    now = datetime.now()
    print("StartTime: "+now.strftime("%d-%b-%Y %H:%M:%S")) 
    print(message+"\n")
 

def processEndMsg(message):
    now = datetime.now()
    print(message)
    print("\nEndTime: "+now.strftime("%d-%b-%Y %H:%M:%S")) 
    print("______________________________________________________________________")