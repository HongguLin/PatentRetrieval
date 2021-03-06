# calculate the recall
def Recall(TP, n):
    R = TP/n
    return R

# calculate the PRES
def PRES(correct, mine, R):
    Nm = len(mine)
    n = len(correct)

    sum=0
    i=0
    for m in mine:
        i = i+1
        if m in correct:
            sum = sum + i

    #sum = sum + R*(Nm+n)-(R*(R-1))/2
    sum = sum +(n-R)*(Nm+n) - (n-R)*(n-R-1)/2
    pres = 1 - (sum/n - (n+1)/2)/Nm
    return pres

# calculate average precision
def AP(correct, mine):
    n = len(correct)
    i=0
    rel_ret=0
    sum=0
    for m in mine:
        i+=1
        if m in correct:
            rel=1
            rel_ret+=1
        else:rel=0
        p = rel_ret/i
        sum = sum + (rel*p)
    rt = sum/n
    return rt

# compare the ground true result and my retrieval result to calculate the average score in three evaluation metrics
def compare(fT, fM):
    result = {}
    All_P = 0
    All_R = 0
    All_A = 0
    T_dict = {}
    M_dict = {}
    with open(fT) as f:
        for line in f:
            PAC = line.split()[0]
            patent = line.split()[2]
            lang = line.split()[4]
            if lang == "EN":
                T_dict.setdefault(PAC,[]).append(patent.split("-")[1])


    with open(fM) as f:
        for line in f:
            PAC = line.split()[0]
            patent = line.split()[2]
            M_dict.setdefault(PAC,[])
            if patent.split("-")[1] not in M_dict[PAC]:
                M_dict[PAC].append(patent.split("-")[1])

    i = 0
    for k, v in T_dict.items():
        if k in M_dict:
            mv_set = set(M_dict[k])
            nv_set = set(T_dict[k])

            TP = len(mv_set & nv_set)

            P = PRES(T_dict[k], M_dict[k], TP)
            R = Recall(TP, len(nv_set))
            A = AP(T_dict[k], M_dict[k])
            result[k] = [P, R, A]
            All_P += P
            All_R += R
            All_A += A
            i = i+1


    N = len(T_dict)
    ave_P = All_P/i
    ave_R = All_R/i
    ave_A = All_A/i
    print("N: ",N)
    print("i: ",i)
    print("A_PRES:",ave_P)
    print("A_Recall",ave_R)
    print("MAP",ave_A)
    print(result)
    return ave_P, ave_R, ave_A

# the main function
def main():
    fm = "result.txt"
    ft = "PAC_qrels_21_EN_mark.txt"
    compare(ft, fm)

if __name__ == '__main__':
    main()

