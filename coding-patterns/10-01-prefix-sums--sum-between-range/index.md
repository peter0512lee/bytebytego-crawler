# Sum Between Range

# Sum Between Range

Given an integer array, write a function which returns the **sum of values between two indexes**.

#### Example:

![Image represents three examples of a `sum_range` function operating on a numerical array `[3, -7, 6, 0, -2, 5]`.  Each example shows the array with indices 0-5 displayed below each element.  The function `sum_range(start_index, end_index)` calculates the sum of elements within a specified range (inclusive). The first example, `sum_range(0, 3)`, highlights elements at indices 0, 1, 2, and 3 (3, -7, 6, 0) in a light-blue box, with a blue arrow above indicating their sum, `sum = 2`. The second example, `sum_range(2, 4)`, highlights elements at indices 2, 3, and 4 (6, 0, -2), showing `sum = 4` above the highlighted section. Finally, `sum_range(2, 2)` highlights only the element at index 2 (6), resulting in `sum = 6`.  In all cases, the function's parameters (start and end indices) are clearly visible, along with the resulting sum displayed above the highlighted portion of the array.](images/sum-between-range-YTKLP363.svg)

```
Input: nums = [3, -7, 6, 0, -2, 5],
       [sum_range(0, 3), sum_range(2, 4), sum_range(2, 2)]
Output: [2, 4, 6]
```

#### Constraints:

* `nums` contains at least one element.
* Each `sum_range` operation will query a valid range of the input array.

## Intuition

We need to code a function `sum_range(i, j)`, where `i` and `j` are the indexes defining the boundaries of the range to be summed up.

A naive solution is to iteratively sum the array values from index `i` to `j`, which takes linear time for each call to `sum_range`. Since we have access to the input array before any calls to `sum_range` are made, we should consider if any **preprocessing** can be done to improve the efficiency of `sum_range`.

This problem deals with subarray sums, so it might be useful to think about how **prefix sums** can be applied to solve it. Consider the integer array below and its prefix sums:

![Image represents a code snippet illustrating the concept of prefix sum.  The top line declares a Python list named `nums` containing the integer values [3, -7, 6, 0, -2, 5].  Below this,  faint gray numbers [0, 1, 2, 3, 4, 5] are shown as indices for the `nums` list. The second line declares another list named `prefix_sum`. This list contains the prefix sums of the `nums` list.  `prefix_sum`'s values are calculated cumulatively: the first element is the same as the first element in `nums` (3), the second is the sum of the first two elements of `nums` (3 + (-7) = -4), the third is the sum of the first three (3 + (-7) + 6 = 2), and so on.  Similarly, faint gray numbers [0, 1, 2, 3, 4, 5] are shown as indices for the `prefix_sum` list, aligning with the corresponding elements in `nums`.  The arrangement visually demonstrates the relationship between an original list and its prefix sum, showing how each element in `prefix_sum` is the cumulative sum of the preceding elements in `nums`.](images/image-10-01-1-VMKJURRC.svg)

We already notice that the prefix sum array has some use: the prefix sum up to any index `j` essentially gives the answer to `sum_range(0, j)`. For example, the sum of the range [0, 3] is just the prefix sum up to index 3:

![Image represents a visual explanation of prefix sum calculation.  The top line shows the equation `sum_range(0, 3) = prefix_sum[3]`, indicating that the sum of elements from index 0 to 3 in an array is equal to the value at index 3 in the prefix sum array. Below, an array named `nums` is shown with values [3, -7, 6, 0, -2, 5], with indices 0 through 5 displayed beneath each element. A light-blue background highlights elements at indices 0, 1, 2, and 3. A cyan-colored line segment above the highlighted portion indicates the range of summation, labeled 'sum = 2,' representing the sum of the highlighted elements (3 + (-7) + 6 + 0 = 2). A downward arrow points from the highlighted section of `nums` to an array named `prefix_sum`.  `prefix_sum` contains the cumulative sums of `nums`; its values are [3, -4, 2, 2, 0, 5], with indices 0 through 5 displayed beneath each element. The value at index 3 in `prefix_sum` (2) matches the calculated sum of `nums` from indices 0 to 3, visually demonstrating the prefix sum concept.](images/image-10-01-2-DJQI5YUH.svg)

Therefore, when `i == 0`:

> `sum_range(0, j) = prefix_sum[j]`

What about when the requested range doesn’t start at 0? Let's say we want to find the sum in the range [2, 4]:

![Image represents a visual depiction of a sub-array within a larger array.  The larger array is shown partially, with elements `[3, -7]` on the left and `[5]` on the right.  These elements are vertically stacked with their indices shown in grey below: `0` and `1` under `[3, -7]` and `5` under `[5]`. The central portion of the image highlights a sub-array `[6, 0, -2]` in a light blue background.  This sub-array's indices are also shown in grey below, indicating positions `2`, `3`, and `4` respectively. The arrangement visually demonstrates how a sub-array is a contiguous section of a larger array, selected by its starting and ending indices.  The indices are used to access specific elements within the array.](images/image-10-01-3-H55BHFLR.svg)

Is there a way to get this using only prefix sums? All prefix sum values are sums for ranges that start at index 0. So, let’s see how we could make use of these ranges. Consider the sum of the range [0, 4], which corresponds to `prefix_sum[4]`:

![Image represents a visual depiction of a sub-array within a larger array.  A light-blue rectangular area displays a numerical array [3, -7, 6, 0, -2], with indices [0, 1, 2, 3, 4] shown faintly below each element.  Above this array, a bright-blue line segment extends horizontally, marked with small perpendicular lines at its ends. A small triangle points downwards from the line segment, positioned above the element '0' at index 3.  The text 'sum[0 : 4]' is written in blue above the line, indicating that a sum is being calculated from index 0 up to (but not including) index 4.  The number '5' is shown outside the light-blue rectangle to the right, likely representing an element beyond the sub-array being considered. The overall image illustrates a sub-array selection and a potential summation operation within a larger array context.](images/image-10-01-4-BKFCNYT4.svg)

The key observation here is that the sum of the range [2, 4] can be obtained by subtracting the sum of the range [0, 1] from the sum above. This can be visualized:

![Image represents a visual depiction of array summation.  A numerical array `[3, -7, 6, 0, -2, 5]` is shown, partitioned into sub-arrays. The first two elements, `[3, -7]`, are highlighted in light gray with red diagonal lines, and a red line segment below indicates their summation, labeled `sum[0: 1]`.  The next three elements, `[6, 0, -2]`, are highlighted in light blue, with a light blue line segment below indicating their summation, labeled `sum[2: 4]`.  A light blue line segment above encompasses the entire array from index 0 to 4, representing the total sum of the array, labeled `sum[0: 4]`. The element at index 5, `5`, is shown separately, not included in any summation.  The indices of each element are subtly indicated below the numbers within the array.](images/image-10-01-5-BSWFQB25.svg)

Since the sums of ranges [0, 4] and [0, 1] are both values in our prefix sum array, we can obtain the sum of the range [2, 4] from the following expression: `prefix_sum[4] - prefix_sum[1]`.

Therefore, when `i > 0`:

> `sum_range(i, j) = prefix_sum[j] - prefix_sum[i - 1]`

Try it yourself

Write your solution to the problem before checking the reference implementation.

[Open Code Editor](/exercises/coding-patterns/prefix-sums/sum-between-range)

## Implementation

Python

JavaScript

Java

```
from typing import List
    
class SumBetweenRange:
    def __init__(self, nums: List[int]):
        self.prefix_sum = [nums[0]]
        for i in range(1, len(nums)):
            self.prefix_sum.append(self.prefix_sum[-1] + nums[i])
    
    def sum_range(self, i: int, j: int) -> int:
        if i == 0:
            return self.prefix_sum[j]
        return self.prefix_sum[j] - self.prefix_sum[i - 1]
```

![](images/copy.3248da0c.svg)

### Complexity Analysis

**Time complexity:** The time complexity of the constructor is O(n)O(n)O(n), where nnn denotes the length of the array. This is because we populate a `prefix_sum` array of length nnn. The time complexity of `sum_range` is O(1)O(1)O(1).

**Space complexity:** The space complexity is O(n)O(n)O(n) due to the space taken up by the `prefix_sum` array.