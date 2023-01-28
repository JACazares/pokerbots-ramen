import eval7
import copy
import random

def get_abstraction(hole=[], board=[]):    
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    cards=hole_cards+board_cards
    sorted_cards=sorted(board_cards, key=lambda x: x.rank)
    suits=[[] for _ in range(4)]
    ranks=[[] for _ in range(13)]
    straights=[]
    high_straights=[]
    straight_flushes=[]
    hand_id=0

    for card in cards:
        r=card.rank
        s=card.suit
        suits[s].append(card)
        ranks[r].append(card)
    for i in range(8):
        high_straights_=[]
        for j0 in ranks[i]:
            for j1 in ranks[i+1]:
                for j2 in ranks[i+2]:
                    for j3 in ranks[i+3]:
                        for j4 in ranks[i+4]:
                            high_straights_.append([j0, j1, j2, j3, j4])
                            straights.append([j0, j1, j2, j3, j4])
                            if (j1.suit == j0.suit and
                                j2.suit == j0.suit and
                                j3.suit == j0.suit and
                                j4.suit == j0.suit):
                                straight_flushes.append([j0, j1, j2, j3, j4])
        if len(high_straights_)>0:
            high_straights=high_straights_

    ranklengths=[len(x) for x in ranks]

    #YOU HAVE STRAIGHT FLUSH_________________________________________________
    if(len(straight_flushes)>0):
        hand_id+=900000
        highest_sf=straight_flushes[-1]
        hole_count=0
        for card in highest_sf:
            if card in hole_cards:
                hole_count+=1
        if(hole_count==0):
            hand_id+=10100
        elif(hole_count==1):
            hand_id+=20100
            if highest_sf[-1] in hole_cards:
                hand_id+=1000
        else: #hole_count==2
            hand_id+=30100
            if highest_sf[-1] in hole_cards:
                hand_id+=1000
                    
    #YOU HAVE POKER__________________________________________________________
    elif(max(ranklengths)>=4):
        hand_id+=800000
        poker=0
        for i in range(13):
            if ranklengths[i]>=4:
                poker=ranks[i]
        hole_count=0

        board_cards_tb=board_cards.copy()
        hole_cards_tb=hole_cards.copy()

        for card in poker:
            if card in hole_cards:
                hole_count+=1
                hole_cards_tb.remove(card)
            else:
                board_cards_tb.remove(card)   

        if(hole_count==0):
            hole_tb=max(hole_cards_tb, key=lambda x: x.rank)
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            hand_id+=10000
            tbrank=max(tbrank, 3)
            if(hole_tb.rank<=tbrank):
                hand_id+=100
            else:
                hand_id+=1000
                dif=hole_tb.rank-tbrank
                if(dif>9):
                    dif=9
                hand_id+=100*dif
        elif(hole_count==1):
            hand_id+=20100
        else: #hole_count==2
            hand_id+=30100

    #YOU HAVE FULL HOUSE_____________________________________________________
    elif(max(ranklengths)==3 and (2 in ranklengths)):
        hand_id+=700000
        fh=[[], []]
        for i in range(13):
            if ranklengths[i]==3:
                fh[0]=ranks[i]
        for i in range(13):
            if ranklengths[i]>=2 and (fh[0] != ranks[i]):
                if ranklengths[i]==3:
                    for card in ranks[i]:
                        if card in board_cards:
                            fh[1].append(card)
                        if len(fh[1])==2:
                            break
                    for card in ranks[i]:
                        if card in hole_cards:
                            fh[1].append(card)
                        if len(fh[1])==2:
                            break
                else: 
                    for card in ranks[i]:
                        fh[1].append(card)
        hole_count=[0, 0]
        hole_third=[]
        hole_pair=[]
        for third_card in fh[0]:
            if third_card in hole_cards:
                hole_count[0]+=1
                hole_third.append(card)
        for pair_card in fh[1]:
            if pair_card in hole_cards:
                hole_count[1]+=1
                hole_pair.append(card)

        if(hole_count==[0, 0]):
            #XXXYY
            hand_id+=100

        elif(hole_count==[0, 1]):
            #XXXY Y
            hand_id+=10000
            non_third_board=sorted(board_cards.copy(), key=lambda x:x.rank)
            our_pair=hole_pair[0]
            for card in non_third_board:
                if card.rank==fh[0][0].rank:
                    non_third_board.remove(card)
            if our_pair.rank>=non_third_board[-1].rank:
                hand_id+=200
            else:
                hand_id+=100

        elif(hole_count==[1, 0]):
            #XXYY X
            hand_id+=20000
            if fh[0][0].rank>fh[1][0].rank:
                hand_id+=200
            else:
                hand_id+=100
        
        elif(hole_count==[2, 0]):
            #XYY XX
            hand_id+=30000
            non_pair_board=sorted(board_cards.copy(), key=lambda x:x.rank)
            our_third=hole_third[0]
            for card in non_pair_board:
                if card.rank==fh[0][0].rank:
                    non_pair_board.remove(card)
            if our_third.rank>=non_pair_board[-1].rank:
                hand_id+=200
            else:
                hand_id+=100
        
        elif(hole_count==[0, 2]):
            #XXX YY
            hand_id+=40000
            non_third_board=sorted(board_cards.copy(), key=lambda x:x.rank)
            our_pair=hole_pair[0]
            for card in non_third_board:
                if card.rank==fh[0][0].rank:
                    non_third_board.remove(card)
            if our_pair.rank>=non_third_board[-1].rank:
                hand_id+=200
            else:
                hand_id+=100

        elif(hole_count==[1, 1]):
            #XXY XY
            hand_id+=50000
            ordered_board=sorted(board_cards.copy(), key=lambda x:x.rank)
            pair_board=[]
            for i in range(len(ordered_board)):
                if(i<len(ordered_board)-1):
                    if(ordered_board[i].rank==ordered_board[i+1].rank):
                        if ordered_board[i] not in pair_board: 
                            pair_board.append(ordered_board[i])
            non_pair_board=[c for c in ordered_board if c not in pair_board]
            x=hole_third[0]
            y=hole_pair[0]
            if(hole_third[0].rank==pair_board[-1].rank):
                if(hole_pair[0].rank==non_pair_board[-1].rank):
                    hand_id+=400
                else:
                    hand_id+=300
            else:
                if(hole_pair[0].rank==non_pair_board[-1].rank):
                    hand_id+=200
                else:
                    hand_id+=100

    #YOU HAVE FLUSH__________________________________________________________
    elif(max([len(x) for x in suits])>=5):
        hand_id+=600000
        flush_suits=[]
        for suit in suits:
            if len(suit)>=5:
                flush_suits.append(suit)

        top_flushes=[]
        for suit in flush_suits:
            ordered_suit=sorted(suit, key=lambda x: x.rank)
            top_flushes.append([ordered_suit[-1], ordered_suit[-2], ordered_suit[-3], ordered_suit[-4], ordered_suit[-5]])
        flush=top_flushes[0]
        for f in top_flushes:
            if f[4]>flush[4]:
                flush=f
            elif f[4]==flush[4] and f[3]>flush[3]:
                flush=f
            elif f[3]==flush[3]  and f[2]>flush[2]:
                flush=f
            elif f[2]==flush[2]  and f[1]>flush[1]:
                flush=f
            elif f[1]==flush[1]  and f[0]>flush[0]:
                flush=f
        suit=flush[0].suit
        if(suit==0 or suit==3):
            hand_id+=10000
        else:
            hand_id+=20000

        hole_count=0
        for card in flush:
            if card in hole_cards:
                hole_count+=1
        if(hole_count==0):
            hand_id+=1000
        elif(hole_count==1):
            hand_id+=2000
        else:
            hand_id+=3000
        if(len(hole_cards)>=2):
            if(hole_cards[0].rank>=flush[3].rank) or (hole_cards[1].rank>=flush[3].rank):
                hand_id+=200
            else: 
                hand_id+=100

    #YOU HAVE STRAIGHT_______________________________________________________
    elif(len(straights)>0):
        hand_id+=500000
        min_hole_count=2
        straight=high_straights[0]
        for st in high_straights:
            hole_count=0
            for card in st:
                if card in hole_cards:
                    hole_count+=1
            if hole_count<min_hole_count:
                straight=st
                min_hole_count=hole_count

        hole_count=min_hole_count
        
        if hole_count==0:
            hand_id+=10100
        elif hole_count==1:
            hand_id+=20000
            if straight[0] in hole_cards:
                hand_id+=100
            elif straight[4] in hole_cards:
                hand_id+=200
            else:
                hand_id+=300
        else: 
            hand_id+=30000
            if straight[4] in hole_cards:
                if straight[3] in hole_cards:
                    hand_id+=400
                else:
                    hand_id+=100
            elif straight[0] in hole_cards:
                if straight[1] in hole_cards:
                    hand_id+=300
                else:
                    hand_id+=200
            else:
                if (straight[1] in hole_cards) and (straight[3] in hole_cards):
                    hand_id+=500
                else:
                    hand_id+=600
    
    #YOU HAVE 3 OF A KIND____________________________________________________
    elif(max(ranklengths)==3):
        hand_id+=400000
        rank=0
        for i in range(13):
            if len(ranks[i])==3:
                rank=i
                third=ranks[i]

        hole_count=0
        board_cards_tb=board_cards.copy()
        hole_cards_tb=hole_cards.copy()
        for card in third:
            if card in hole_cards:
                hole_count+=1
                hole_cards_tb.remove(card)
            else:
                board_cards_tb.remove(card) 
         
        if hole_count==0:
            hand_id+=10000
            hole_tb=max(hole_cards_tb, key=lambda x: x.rank)
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            if(hole_tb.rank<=tbrank):
                hand_id+=100
            else:
                hand_id+=1000
                dif=hole_tb.rank-tbrank
                if(dif>9):
                    dif=9
                hand_id+=100*dif

        elif hole_count==1:
            hand_id+=20000
            highest_pair_rank=rank
            for card in board_cards:
                if len(ranks[card.rank])>=2 and highest_pair_rank<card.rank:
                    highest_pair_rank=card.rank
            hole_tb=max(hole_cards_tb, key=lambda x: x.rank)
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            if rank==highest_pair_rank:
                if hole_tb.rank>=tbrank:
                    hand_id+=400
                else:
                    hand_id+=200
            else:
                if hole_tb.rank>=tbrank:
                    hand_id+=300
                else:
                    hand_id+=100
            
        else: #hole_count==2
            hand_id+=30000
            highest_pair_rank=rank
            for card in board_cards:
                if len(ranks[card.rank])>=2 and highest_pair_rank<card.rank:
                    highest_pair_rank=card.rank
            if rank>=highest_pair_rank:
                hand_id+=200
            else:
                hand_id+=100

    #YOU HAVE 2 PAIRS________________________________________________________
    elif(2==sorted(ranklengths)[-2]):
        hand_id+=300000
        pair_ranks=[]
        for rank in ranks:
            if len(rank)>=2:
                pair_ranks.append(rank)
        high=pair_ranks[-1]
        low=pair_ranks[-2]
        hole_distribution=[0, 0]
        for card in cards:
            if card in hole_cards:
                if card in low:
                    hole_distribution[1]+=1
                if card in high:
                    hole_distribution[0]+=1
        
        board_cards_tb=board_cards.copy()
        hole_cards_tb=hole_cards.copy()
        for card in low+high:
            if card in hole_cards:
                hole_cards_tb.remove(card)
            else:
                board_cards_tb.remove(card)
                
        
        if hole_distribution==[0, 2] or hole_distribution==[2, 0]:
            hand_id+=10000
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            
            if hole_cards[0].rank>=tbrank:
                hand_id+=200
            else:
                hand_id+=100

        elif hole_distribution==[0, 0]:
            hand_id+=20000
            hole_tb=max(hole_cards_tb, key=lambda x: x.rank)
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            if(hole_tb.rank<=tbrank):
                hand_id+=100
            else:
                hand_id+=1000
                dif=hole_tb.rank-tbrank
                if(dif>9):
                    dif=9
                hand_id+=100*dif
        elif hole_distribution==[0, 1] or hole_distribution==[1, 0]:
            hand_id+=30000#mal implementado
            hole_tb=max(hole_cards_tb, key=lambda x: x.rank)
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            if hole_cards[0] in high or hole_cards[0] in low:
                Yhole=hole_cards[0]
                hole_tb=hole_cards[1]
            else:
                Yhole=hole_cards[0]
                hole_tb=hole_cards[1]
            if Yhole.rank>tbrank:
                if hole_tb.rank>tbrank:
                    hand_id+=600
                else:
                    hand_id+=500
            elif Yhole.rank==tbrank:
                if hole_tb.rank>tbrank:
                    hand_id+=400
                else:
                    hand_id+=300
            else:
                if hole_tb.rank>tbrank:
                    hand_id+=200
                else:
                    hand_id+=100
        else: #hole_distribution=[1, 1]
            hand_id+=40000
            if hole_cards[0]>hole_cards[1]:
                X=hole_cards[0]
                Y=hole_cards[1]
            else: 
                X=hole_cards[1]
                Y=hole_cards[0]
            if X>=sorted_cards[-1]:
                if Y>=sorted_cards[-2]:
                    hand_id+=400
                else: 
                    hand_id+=300
            elif X==sorted_cards[-2]:
                hand_id+=200
            else: 
                hand_id+=100

    #YOU HAVE 1 PAIR__________________________________________________________
    elif(2 in ranklengths):
        hand_id+=200000
        for rank in ranks:
            if len(rank)>1:
                pair=rank
        hole_count=0
        board_cards_tb=board_cards.copy()
        hole_cards_tb=hole_cards.copy()
        for card in pair:
            if card in hole_cards:
                hole_count+=1
                hole_cards_tb.remove(card)
            else: 
                board_cards_tb.remove(card) 

        if hole_count==0:
            hand_id+=10000
            rank=hole_cards[0].rank
            if(len(board_cards_tb)>0):
                board_tb=max(board_cards_tb, key=lambda x: x.rank)
                tbrank=board_tb.rank
            else: 
                tbrank=2
            tbrank=max(tbrank, 3)
            if(rank<=tbrank):
                hand_id+=100
                dif=tbrank-rank
                if dif>9:
                    dif=9
                hand_id+=100*dif
            else:
                hand_id+=1000
                dif=rank-tbrank
                if(dif>9):
                    dif=9
                hand_id+=100*dif

        elif hole_count==1:
            hand_id+=20000
            if hole_cards[0] in pair:
                pair_card=hole_cards[0]
                hole_tb=hole_cards[1]
            else: 
                pair_card=hole_cards[1]
                hole_tb=hole_cards[0]
            for i in range(10):
                if len(sorted_cards)>=i+1:
                    if pair_card.rank==sorted_cards[-i-1].rank:
                        hand_id+=(9-i)*1000
            if hole_tb.rank>=4:
                hand_id+=(hole_tb.rank-3)*100

        else: #hole_count==2
            hand_id+=30000
            hole_tb=max(hole_cards, key=lambda x: x.rank)
            hand_id+=(hole_tb.rank+2)*100 #2-14
   
   #YOU HAVE NOTHING_________________________________________________________
    else:
        hand_id+=100000
        board_cards_tb=board_cards.copy()
        
        hole_tb=max(hole_cards, key=lambda x: x.rank)
        if(len(board_cards)>0):
            board_tb=max(board_cards, key=lambda x: x.rank)
            tbrank=board_tb.rank
        else: 
            tbrank=2
        tbrank=max(tbrank, 3)
        if(hole_tb.rank<=tbrank):
            hand_id+=100
            dif=tbrank-hole_tb.rank
            if dif>9:
                dif=9
            hand_id+=100*dif
        else:
            hand_id+=1000
            dif=hole_tb.rank-tbrank
            if(dif>9):
                dif=9
            hand_id+=100*dif
    
    return hand_id
    
if __name__=="__main__":
    for i in range(1000):
        deck=eval7.Deck()
        deck.shuffle()
        b=random.randint(3, 10)
        hole_cards=deck.deal(2)
        board_cards=deck.deal(b)
        hole=list(map(str, hole_cards))
        board=list(map(str, board_cards))
        print(f"iteration {i}")
        print(f"hole: {hole}")
        print(f"board: {board}")
        hand_id=get_abstraction(hole, board)
        print(f"hand_id: {hand_id}")
        print(" ")
        




    