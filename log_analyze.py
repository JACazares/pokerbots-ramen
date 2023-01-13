import re
import matplotlib.pyplot as plt

def read_gamelog(filename):
    with open(filename) as f:
        raw_data = f.readlines()
    
    scoresA = []
    scoresB = []
    for line in raw_data:
        lineAB = re.match("Round #[0-9]*, A \((-?[0-9]*)\), B \((-?[0-9]*)\)", line)
        lineBA = re.match("Round #[0-9]*, B \((-?[0-9]*)\), A \((-?[0-9]*)\)", line)
        if lineAB:
            scoresA.append(int(lineAB.group(1)))
            scoresB.append(int(lineAB.group(2)))
        elif lineBA:
            scoresA.append(int(lineBA.group(2)))
            scoresB.append(int(lineBA.group(1)))
    
    return (scoresA, scoresB)

if __name__ == "__main__":
    scoreA, scoreB = read_gamelog("gamelog.txt")
    plt.plot(list(range(1, len(scoreA)+1)), scoreA, marker='o', linestyle='-', markersize=2, color="red")
    plt.title("Player A")
    #plt.plot(list(range(1, len(scoreB)+1)), scoreB, marker='o', linestyle='-', markersize=2, color="blue")
    plt.show()
    pass