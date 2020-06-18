#The Epoch is Jan 1 1970 8 PM
#Market open from 9:30 AM to 4 PM
#So hour must be between 13.5 and 20
while not(13.5 < time.time()%86400/60/60 < 20):
    time.sleep(60)
