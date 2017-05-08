weights = [0.1, 0.2, 0]
toes = [8.5, 9.5, 9.9, 9]
wlrec = [0.65, 0.8, 0.8, 0.9]
nfans = [1.2, 1.3, 0.5, 1]

def neural_networks(input, weights):
    pred = w_sum(input, weights)
    return pred

def w_sum(input, weights):
    assert(len(input)==len(weights))
    output = 0
    for i,j in zip(input,weights):
        output += (i * j)
    return output

input = [toes[0], wlrec[0], nfans[0]]
pred = neural_networks(input, weights)

print(pred)
