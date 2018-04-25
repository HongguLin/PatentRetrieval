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
            R = ARecall(TP, len(nv_set))
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

def ARecall(TP, n):
    R = TP/n
    return R

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


def sort(fM, fN):
    P_dict = {}
    with open(fM) as f:
        for line in f:
            PAC = line.split()[0]
            patent = line.split()[2]
            P_dict.setdefault(PAC,[]).append(patent)

    tmp = sorted(P_dict.items(),key=lambda x:int(x[0].split("-")[1]))

    with open(fN, 'a') as f:
        for key, value in tmp:
            for v in value:
                f.write(key+" 0 "+v+" 1\n")

def main():
    fm = "/Users/linhonggu/Desktop/result.txt"
    #fn = "/Users/linhonggu/Desktop/sortedResult.txt"
    ft = "/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN_mark.txt"
    #sort(fm,fn)
    compare(ft, fm)


if __name__ == '__main__':
    main()

