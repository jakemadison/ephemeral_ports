# this script is an attempt to test a client report of "no sockets" to confirm if they are not
# not receiving data because they have run out of socket space on their side
# because of TCP TIME_WAITs.
# see: http://www.ncftp.com/ncftpd/doc/misc/ephemeral_ports.html

#create a connection class for every line item.
#that class has a TTL which counts down until zero and then dies
#we have max connections = 4000 as a global
#and we have total time which just counts up from start time.

#okay so problems here: change in network speed, number of other requests going on
#anything DB related, anything else client-related

max_conn = 4000
mainclock = 1500
req_array = []


class Request():

    global_ttl = float(240) + float(5)  # 240 is IP stack standard TIME_WAIT

    def __init__(self, size):
        self.ttl = float(Request.global_ttl + (0.025*float(size)))  # size needs tweaking.
        self.active = True

    def decrement_life(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.active = False

    def get_my_ttl(self):
        print self.ttl


# add a new request to our array, decrement max connections
def make_req(size):
    req_array.append(Request(size))
    global max_conn
    max_conn -= 1


#move forward in time, decrease everyone's life
#then for any that are dead now, set active to false and
#get rid of them.
def advance_time():

    global max_conn
    if len(req_array) > 0:
        for r in req_array:
            r.decrement_life()

        for r in req_array:
            if not r.active:
                req_array.remove(r)
                #print 'deleting instance', max_conn
                max_conn += 1


#convert our timestamps to seconds:
def stamp_to_secs(stamp):
    if stamp:
        h, m, s = stamp.split(':')
        secs = (int(h)*60*60)+(int(m)*60)+int(s)
        return int(secs)


#open our file, split up timestamp and size information
f = open('./timesnew_sorted', 'r')

thisone = f.readline().replace('\n', '')
thistime, thissize = thisone.split(' ')
nextval = stamp_to_secs(thistime)
conold = max_conn


#I don't care about the earlier values, skip to mass influx:
starter = '16:01:48'

#cue us up:
while thistime.strip() != starter:
    thisone = f.readline().replace('\n', '')
    thistime, thissize = thisone.split(' ')
    nextval = stamp_to_secs(thistime)


#main loop:
lowestval = max_conn

while True:
    while mainclock == nextval:

        make_req(thissize)

        # get a new line item:
        thisone = f.readline().replace('\n', '')

        #check for EOF marker
        if '#' in thisone:
            print 'Made it through without breakage'
            print 'lowests', lowestval, lowesttime
            exit()

        thistime, thissize = thisone.split(' ')
        nextval = stamp_to_secs(thistime)

    advance_time()

    #check for change in max conns and notify:
    if conold != max_conn:
        print 'cons: ', max_conn, 'clock: ', mainclock, 'time: ', thistime, 'size: ', thissize
        if max_conn < lowestval:
            lowestval = max_conn
            lowesttime = thistime

    #see if we have run out of connections. (really this should be higher as well, but whatever)
    if max_conn <= 0:
        print 'BREAK BREAK BREAK!', max_conn
        print 'lowest vals: ', lowestval, lowesttime
        exit()


    conold = max_conn
    mainclock += 1


f.close()
