
def pivot_sort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]  # Choosing the pivot element
    left = [x for x in arr if x < pivot]  # Elements less than pivot
    middle = [x for x in arr if x == pivot]  # Elements equal to pivot
    right = [x for x in arr if x > pivot]  # Elements greater than pivot

    return pivot_sort(left) + middle + pivot_sort(right)

# Example to test the pivot_sort function
sample_data = [38, 27, 43, 3, 9, 82, 10]
sorted_data = pivot_sort(sample_data)
print('Sorted array is:', sorted_data)
