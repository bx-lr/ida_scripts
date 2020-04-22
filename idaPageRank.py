import operator
import numpy as np
from scipy.sparse import csc_matrix
from UserDict import UserDict

class odict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)


def pageRank(G, s = .85, maxerr = .001, loops = 80):
    #G must be a square matrix
    n = G.shape[0]

    # transform G into markov matrix M
    M = csc_matrix(G,dtype=np.float)
    rsums = np.array(M.sum(1))[:,0]
    ri, ci = M.nonzero()
    M.data /= rsums[ri]

    # bool array of sink states
    sink = rsums==0

    # Compute pagerank r until we converge
    # or reach a local minimum state
    ro, r = np.zeros(n), np.ones(n)
    last_sum = 999999999
    for _ in xrange(loops):
        if last_sum < maxerr:
            break
        ro = r.copy()
        # calculate each pagerank at a time
        for i in xrange(0,n):

            # inlinks of state i
            Ii = np.array(M[:,i].todense())[:,0]

            # account for sink states
            Si = sink / float(n)

            # account for teleportation to state i
            Ti = np.ones(n) / float(n)
            r[i] = ro.dot( Ii*s + Si*s + Ti*(1-s) )

        csum = np.sum(np.abs(r-ro))
        if csum < last_sum:
            #print 'Current Convergence csum', csum
            last_sum = csum
        else:
            break

    # return normalized pagerank
    return r/sum(r)
    

ea = ScreenEA()
od = odict()
print "Building Function List..."

#np.set_printoptions(threshold='nan')

for funcea in Functions(SegStart(ea), SegEnd(ea)):
    functionName = GetFunctionName(funcea)
    tmp = []
    for ref in CodeRefsTo(funcea, 1):
            tmp.append(GetFunctionName(ref))
    od[functionName] = tmp

print 'Populating XREF Matrix'
num_funcs = len(od.keys())
links = np.zeros(shape=(num_funcs,num_funcs))
for i in xrange(0,num_funcs):
    key = od.keys()[i]
    vals = od[key]
    #print i, key, vals
    for v in vals:
        if len(v) > 0:
            #if v not in od.keys():
            #    continue
            idx = od.keys().index(v)
            #print 'i', i, 'idx', idx
            #print i, key, v, idx
            links[i][idx] = 1


###### testing code ######
#
#links = np.zeros(shape=(2,2))
#two node 1 link test
#links[0][1]=1 #a,b
#
#links = np.zeros(shape=(3,3))
#circle test
#links[0][1]=1 # a,b
#links[1][2]=1 # b,c
#links[2][0]=1 # c,a
#
#links = np.zeros(shape=(6,6))
#2 circle test
#links[0][1]=1 # a,b
#links[1][2]=1 # b,c
#links[2][0]=1 # c,a
#links[3][4]=1 # d,e
#links[4][5]=1 # e,f
#links[5][3]=1 # f,d
#
#links = np.zeros(shape=(5,5))
#n to n+1 test
#links[0][1]=1 #a,b
#links[0][2]=1 #a,c
#links[1][2]=1 #b,c
#links[2][3]=1 #c,d
#links[3][4]=1 #d,e
#links[4][0]=1 #e,a
#
#print 'matrix: \n', links
#print 'matrix(t): \n', links.transpose()
#print '\npr: ', pageRank(links)

print 'Calculating Rank: %dx%d' % (num_funcs, num_funcs) 


rank = pageRank(links)
for i in xrange(0, num_funcs):
    od[od.keys()[i]] = rank[i]
    #print od.keys()[i], rank[i], links[i]


sorted_r = sorted(od.iteritems(), key=operator.itemgetter(1), reverse=True)
for tup in sorted_r:
    print '{0:10} :{1:30}'.format(tup[0], str(tup[1]))


