n = int(input())

primes = (i for i in range(2, n) if i == 2 or (not i % 2 == 0 and not any(j for j in range(2, i) if i % j == 0)))

for p in primes:
    print(p)
