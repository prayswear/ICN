import pickle

a=[1,2,3]
b='asb'
try:
    with open('mytest.txt','wb') as myfile:
        pickle.dump(a,myfile)
        pickle.dump(b,myfile)
except IOError as e:
    print(e)

try:
    with open('mytest.txt','rb') as readfile:
        c=pickle.load(readfile)
        d=pickle.load(readfile)
        print(c)
        print(d)
except IOError as e:
    print(e)
