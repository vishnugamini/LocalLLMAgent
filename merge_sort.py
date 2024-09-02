
import os  # Importing os module

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        print('Left half:', left_half)
        print('Right half:', right_half)

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

        print('Merged array:', arr)

if __name__ == '__main__':
    print('Starting program...')
    user_input = input('Enter numbers separated by spaces: ')
    print(f'Raw user input: {user_input}')
    numbers = list(map(int, user_input.split()))
    print('Original numbers:', numbers)
    merge_sort(numbers)
    print('Sorted numbers:', numbers)
