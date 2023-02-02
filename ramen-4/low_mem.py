import pickle

with open('strategy.pickle', 'rb') as f:
    strategy=pickle.load(f)

strategy2={}
for k, v in strategy.items(): 
    if k[1]>=6:
        continue
    strategy2[k]=v
with open('low_mem.pickle', 'wb') as f:
    pickle.dump(strategy2, f)
    

