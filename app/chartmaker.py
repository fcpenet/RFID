import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
'''
#change these 2 variables to suit your needs
nPass = 5857
nFail = 1362

plt.pie([nPass, nFail],
                colors=["green","red"],
                        labels=["Pass", "Fail"],
                                autopct='%1.1f%%',
                                        startangle=90)

plt.axis('equal') #ensure pie is round
plt.show()
'''


class ChartMaker():
    def plotPie(self, info, message):
        countlist = []
        labellist = []
        for item in info:
            for key in item.keys():
                if('count'==key):
                    countlist.append(item[key])
                else:
                    labellist.append(item[key])

        count = len(labellist)
        a=np.random.random(count)
        cs=cm.Set1(np.arange(count)/count)
        p, tx, autotexts = plt.pie(countlist,labels=labellist, colors=cs, autopct='%1.1f%%', startangle=90)

        for i,a in enumerate(autotexts):
            a.set_text("{}({})".format(a.get_text(), countlist[i]))
        plt.axis('equal')
        plt.text(-1.5,-1.3, message, fontsize=10)
        plt.show()

