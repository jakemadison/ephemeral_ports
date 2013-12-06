# this script is an attempt to test a client report of "no sockets" to confirm if they are not
# not receiving data, because they have run out of socket space on their side
# because of TCP TIME_WAITs.
# see: http://www.ncftp.com/ncftpd/doc/misc/ephemeral_ports.html



#create a connection class for every line item.
#that class has a TTL which counts down until zero and then dies
#we have max connections = 4000 as a global
#and we have total time which just counts up from start time.


#okay, this is better done either as threads (gross) or with the main event loop in the outer block
#and a simple method to decrement
import time

max_conn = 4000
mainclock = 1500
req_array = []


class Request():

    global_ttl = float(240) + float(5)

    def __init__(self, size):
        self.ttl = float((Request.global_ttl) + (0.025*float(size)))
        #print self.ttl
        self.active = True

    def decrement_life(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.active = False

    def get_my_ttl(self):
        print self.ttl


def make_req(size):
    req_array.append(Request(size))
    global max_conn
    max_conn -= 1


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


def stamp_to_secs(stamp):
    if stamp:
        h, m, s = stamp.split(':')
        secs = (int(h)*60*60)+(int(m)*60)+int(s)
        return int(secs)



f = open('./timesnew_sorted', 'r')



thisone = f.readline().replace('\n', '')
thistime, thissize = thisone.split(' ')

nextval = stamp_to_secs(thistime)
conold = max_conn

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
        #print 'creating new instance'
        make_req(thissize)
        thisone = f.readline().replace('\n', '')

        if '#' in thistime.strip():
            print 'Made it through without breakage'
            print 'lowests', lowestval, lowesttime
            exit()


        thistime, thissize = thisone.split(' ')
        nextval = stamp_to_secs(thistime)

    advance_time()

    if conold != max_conn:
        print 'cons: ', max_conn, 'clock: ', mainclock, 'time: ', thistime, 'size: ', thissize
        if max_conn < lowestval:
            lowestval = max_conn
            lowesttime = thistime

    if max_conn <= 0:
        print 'BREAK BREAK BREAK!', max_conn
        print 'lowests', lowestval, lowesttime


        #for each in req_array:
         #   print each.ttl


        exit()


    conold = max_conn
    mainclock += 1
    #print mainclock




f.close()





#
#
# for x in range(0,10):
#     print "creating instance     ", x
#     req_array.append(Request())
#     if len(req_array) > 0:
#         for each in req_array:
#             each.decrement_life()
#
#
#
#
#
# for each in req_array:
#     print each.active
#     print each.ttl
