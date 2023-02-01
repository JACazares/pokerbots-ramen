try:
    with open('strategy.txt') as f:
        st = eval(f.read())
except:
    st = {}