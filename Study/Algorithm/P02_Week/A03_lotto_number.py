M = 30
N = 3

default_list = []
cnt = 0

for i in range(1, round(M/pow(2, N-1))+1):
    if (i * pow(2, N-1)) <= M:
        temp = []
        for j in range(N):
            temp.append(i*pow(2, j))
        default_list.append(temp)
    else:
        break

print(default_list)

test = [1, 2, 4, 8]

N = 4
M = 30

for i in range(0, N-2):
    print([M-(2*n)+1 for n in range(pow(2, N-1), int(M/2)) if n <= M])

# [1, 2]


# [1, 2, 4] = 30-4+1, [1, 3, 6] = 30-6+1, [1, 4, 8] = 30-8+1, [1, 5, 10] = 30-10+1


# [1, 2, 4, 8]   = 30-8+1,  [1, 2, 5, 10] = 30-10+1, [1, 2, 6, 12] = 30-12+1 ... [1, 2, 15, 30] = 30-30+1
# [1, 3, 6, 12]  = 30-12+1, [1, 3, 7, 14] = 30-14+1,
# [1, 4, 8, 16]  = 30-16+1
# [1, 5, 10, 20] = 30-20+1
# [1, 6, 12, 24] = 30-24+1


# [1, 2, 4, 8, 16]  = 50-16+1, [1, 2, 4, 9, 18]  = 50-18+1
# [1, 2, 5, 10, 20] = 50-20+1, [1, 2, 5, 11, 22] = 50-22+1
# [1, 2, 6, 12, 24] = 50-24+1, [1, 2, 6, 13, 26] = 50-26+1

# [1, 3, 6, 12, 24] = 50-24+1, [1, 3, 6, 13, 26] = 50-26+1
# [1, 3, 7, 14, 28] = 50-28+1,

# [1, 4, 8, 16, 32] = 50-32+1, [1, 4, 8, 17, 34] = 50-34+1


# [1, 2, 4, 8, 16, 32] = 50-32+1, [1, 2, 4, 8, 17, 34] = 50-34+1
# [1, 2, 4, 9, 18, 36] = 50-36+1

# [1, 2, 5, 10, 20, 40] = 50-40+1
# [1, 2, 5, 11, 22, 44] = 50-44+1
# [1, 2, 6, 12, 24, 48] = 50-48+1

# [1, 3, 6, 12, 24, 48] = 50-48+1