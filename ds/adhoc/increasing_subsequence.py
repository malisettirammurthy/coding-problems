# Write a program to find the Increasing sub sequence in a given array of integers.
def increasing_subsequence(arr):
    n = len(arr)
    if n == 0:
        return []

    # Initialize the list to store the longest increasing subsequence
    lis = [1] * n
    prev = [-1] * n

    # Compute the length of LIS for each element
    for i in range(1, n):
        for j in range(i):
            if arr[i] > arr[j] and lis[i] < lis[j] + 1:
                lis[i] = lis[j] + 1
                prev[i] = j

    # Find the maximum length of LIS
    max_length = max(lis)
    max_index = lis.index(max_length)

    # Reconstruct the longest increasing subsequence
    sequence = []
    while max_index != -1:
        sequence.append(arr[max_index])
        max_index = prev[max_index]

    sequence.reverse()
    return sequence

if __name__ == "__main__":
    arr = [6,4, 7,2,1,8]
    print(increasing_subsequence(arr))
