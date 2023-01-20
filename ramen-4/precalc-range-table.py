import eval7


#aaaaaaaaaaaaaaaaaa ifelsebot
def range_table():
    deck = eval7.Deck()
    hand_range = {}
    for i in range(52):
        for j in range(i, 52):
            if i == j:
                pass
            r = (str(deck.cards[i])[0], str(deck.cards[j])[0])
            s = (str(deck.cards[i])[1], str(deck.cards[j])[1])

            ans = 8
            # Pairs
            if r[0] == r[1]:
                if r[0] == '2':
                    ans = 5
                elif '3' <= r[0] and r[0] <= '5':
                    ans = 3
                elif '6' <= r[0] and r[0] <= '7':
                    ans = 2
                else:
                    ans = 1
            # Suited
            elif s[0] == s[1]:
                if r[0] == '2':
                    if r[1] in ['3', '4', '5', '6', '7']:
                        ans = 8
                    elif r[1] in ['8', '9', 'T']:
                        ans = 7
                    elif r[1] in ['J', 'Q', 'K']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '3':
                    if r[1] in ['4', '5', '6', '7']:
                        ans = 8
                    elif r[1] in ['8', '9']:
                        ans = 7
                    elif r[1] in ['T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '4':
                    if r[1] in ['5', '6']:
                        ans = 8
                    elif r[1] in ['7', '8', '9']:
                        ans = 7
                    elif r[1] in ['T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '5':
                    if r[1] in ['6', '7', '8', '9', 'T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '6':
                    if r[1] in ['7', '8', '9', 'T']:
                        ans = 6
                    elif r[1] in ['J']:
                        ans = 5
                    elif r[1] in ['Q']:
                        ans = 4
                    else:
                        ans = 3
                elif r[0] == '7':
                    if r[1] in ['8', '9']:
                        ans = 6
                    elif r[1] in ['T', 'J', 'Q']:
                        ans = 4
                    elif r[1] in ['K']:
                        ans = 3
                    else:
                        ans = 2
                elif r[0] == '8':
                    if r[1] in ['9']:
                        ans = 6
                    elif r[1] in ['T', 'J', 'Q']:
                        ans = 4
                    elif r[1] in ['K']:
                        ans = 3
                    else:
                        ans = 2
                elif r[0] == '9':
                    if r[1] in ['T', 'J', 'Q']:
                        ans = 4
                    else:
                        ans = 2
                elif r[0] == 'T':
                    if r[1] in ['J']:
                        ans = 4
                    else:
                        ans = 2
                else:
                    ans = 2
            # Off Suit
            else:
                if r[0] == '2':
                    if r[1] in ['3', '4', '5', '6', '7', '8']:
                        ans = 8
                    elif r[1] in ['9', 'T', 'J']:
                        ans = 7
                    elif r[1] in ['Q', 'K']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '3':
                    if r[1] in ['4', '5', '6', '7', '8']:
                        ans = 8
                    elif r[1] in ['9', 'T', 'J']:
                        ans = 7
                    elif r[1] in ['Q', 'K']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '4':
                    if r[1] in ['5', '6', '7']:
                        ans = 8
                    elif r[1] in ['8', '9', 'T']:
                        ans = 7
                    elif r[1] in ['J', 'Q', 'K']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '5':
                    if r[1] in ['6']:
                        ans = 8
                    elif r[1] in ['7', '8', '9', 'T']:
                        ans = 7
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '6':
                    if r[1] in ['7', '8', '9', 'T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '7':
                    if r[1] in ['8', '9', 'T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 5
                    else:
                        ans = 3
                elif r[0] == '8':
                    if r[1] in ['9', 'T']:
                        ans = 6
                    elif r[1] in ['J', 'Q']:
                        ans = 4
                    else:
                        ans = 3
                elif r[0] == '9':
                    if r[1] in ['T', 'J', 'Q']:
                        ans = 4
                    elif r[1] in ['K']:
                        ans = 3
                    else:
                        ans = 2
                elif r[0] == 'T':
                    if r[1] in ['J', 'Q']:
                        ans = 4
                    elif r[1] in ['K']:
                        ans = 3
                    else:
                        ans = 2
                elif r[0] == 'J':
                    if r[1] in ['Q']:
                        ans = 4
                    else:
                        ans = 2
                else:
                    ans = 2

            hand_range[(str(deck.cards[i]), str(deck.cards[j]))] = ans
            hand_range[(str(deck.cards[j]), str(deck.cards[i]))] = ans
    
    return hand_range


if __name__ == "__main__":
    hand_range = range_table()
    print(hand_range)
    pass