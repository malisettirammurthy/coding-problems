# Write a program to find if there exists a subsequence of size 3 in an array such that
# the elements of the subsequence are in increasing order, i.e., a[i] < a[j] < a[k] where i < j < k.

def subsequence(arr):
    min1 = max(arr)
    min2 = max(arr)
    for x in arr:
        if x < min1:
            min1 = x
        elif x < min2:
            min2 = x
        else:
            print(min1, min2, x)
            return True

if __name__ == "__main__":
    arr = [6,7,2,1,8]
    print(subsequence(arr))