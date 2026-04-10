# Combinations of a Sum

# Combinations of a Sum

Given an integer array and a target value, find **all unique combinations** in the array where the numbers in each combination sum to the target. Each number in the array may be used an unlimited number of times in the combination.

#### Example:

```
Input: nums = [1, 2, 3], target = 4
Output: [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2]]
```

#### Constraints:

* All integers in nums are positive and unique.
* The target value is positive.
* The output must not contain duplicate combinations. For example, `[1, 1, 2]` and `[1, 2, 1]` are considered the same combination.

## Intuition

Since we can use each integer in the input array as many times as we like, we can create an infinite number of combinations. We certainly cannot explore combinations infinitely. So, to manage this, we need to narrow our search.

An important point that will help us with this is that all values in the integer array are positive integers. This means that as we add more values to a combination, its sum will increase. Therefore, we should **stop building a combination once its sum is equal to or exceeds the target value**.

Another thing we should be mindful of is duplicate combinations. Consider the input array [1, 2, 3]. The combinations [1, 3, 2, 1] and [2, 1, 3, 1] represent the same combination. To ensure a **universal representation**, we can represent this combination as [1, 1, 2, 3], where the integers appear in the same order as in the original array. To ensure every combination has only one version, we need to build the combinations so that they are all ordered this way.

With those two things in mind, let's think about how we find all combinations that sum to the target value. **Backtracking** is ideal for exploring all possible combinations, so let's start by considering the state space tree for this problem.

**State space tree**  
The purpose of a state space tree is to show combinations getting built one number at a time. Consider the input array [1, 2, 3] and a target of 4. Let's start with the root node of the tree, which is an empty combination:

![Image represents a pair of large, black, square brackets, oriented vertically with a significant space between them.  Each bracket is composed of three distinct, thick, parallel lines creating a solid, shadowed appearance suggesting depth. The brackets are positioned symmetrically, with the left bracket mirroring the right bracket in size, shape, and shadowing.  No text, URLs, or parameters are present within or around the brackets; the image solely depicts the brackets themselves, implying a visual representation of a code block or a structural element within a programming context, likely used to denote the beginning and end of a code section or a data structure. The empty space between the brackets suggests the content that would typically be enclosed within them in a programming language.](images/image-14-04-1-AQATP6WP.svg)

To figure out how to branch out from here, let's identify what decisions we can make. Each element can be included in a combination an unlimited number of times. So, this means we can make three decisions for an array of length 3: include each element from the array (remember that a branch in the state space tree represents a decision):

![Image represents a decision tree illustrating a choice between three options.  A central node, labeled '[]' (representing the decision point), branches out to three leaf nodes labeled '[1]', '[2]', and '[3]'.  Each branch is labeled with the text 'choose' in orange, followed by a number (1, 2, or 3) indicating the selected option.  Arrows point from the central node to each leaf node, signifying the flow of control based on the choice made.  The numbers 1, 2, and 3 represent the three possible outcomes or paths resulting from the decision at the central node.  The square brackets around the leaf node labels might indicate an array or list structure in a programming context.](images/image-14-04-2-2QU2VSXF.svg)

Let's make the same decisions for each of these combinations as well to continue extending the state space tree. Remember that if any combination has a sum equal to 4 or exceeding 4, we stop extending those combinations. These two conditions are effectively our termination conditions:

![Image represents a tree-like structure illustrating a recursive algorithm, possibly for finding combinations. The root node is an empty array `[]`.  From the root, three branches extend, labeled with orange numbers 1, 2, and 3, respectively, pointing to nodes `[1]`, `[2]`, and `[3]`. Each of these nodes further branches into three sub-nodes, again labeled 1, 2, and 3, resulting in leaf nodes representing two-element arrays like `[1,1]`, `[1,2]`, `[1,3]`, etc.  Each leaf node displays the sum of its elements.  A green checkmark indicates that the sum equals 4, while a red 'X' signifies a sum greater than 4. Dashed lines connect the leaf nodes to unseen underlying elements, suggesting further recursion or exploration of possibilities. The orange numbers on the branches seem to represent the values being added to the array at each level.](images/image-14-04-3-U4RY44YX.svg)

One issue with this approach is that it resulted in duplicate combinations in our tree:

![Image represents a tree-like structure illustrating a coding pattern, possibly related to recursion or tree traversal.  The root node is labeled `[]`, representing an empty array or the starting point.  From the root, three branches descend, each labeled `[1]`, `[2]`, and `[3]`, respectively. Each of these nodes further branches into three child nodes, representing arrays with two elements. For example, `[1]` branches into `[1,1]`, `[1,2]`, and `[1,3]`.  The nodes `[2,1]`, `[3,1]`, and `[3,2]` are highlighted in a peach/light orange color. Curved arrows connect certain pairs of these leaf nodes, labeled 'duplicate' in a corresponding color (peach/light orange for the peach/light orange nodes, and gold for the other nodes). These arrows indicate that the connected nodes represent duplicate or redundant data structures within the overall pattern.  The structure visually demonstrates how different combinations of elements can arise from a recursive or iterative process, and highlights the identification and handling of duplicate results.](images/image-14-04-4-WF6TDWC7.svg)

To avoid these duplicates, we should keep in mind our universal representation: each combination should be constructed such that its elements are listed in the same order as in the input array. We can enforce this by specifying an index '**`start_index`**' for each combination we create. This `start_index` points to a value in the input array and ensures that we can only add elements from this value onward. This way, we maintain the correct order and avoid duplicates in our combinations:

![Image represents a tree-like structure illustrating a recursive algorithm, possibly for finding subsets of an array `nums = [1, 2, 3]` that sum to 4.  The root node is `[], start_index = 0`, representing an empty subset and a starting index of 0.  From the root, three branches extend, each representing a subset starting with one of the elements from `nums`.  Each node shows the current subset (e.g., `[1]`, `[2]`, `[3]`) and its `start_index`.  These nodes further branch, recursively adding subsequent elements from `nums` (starting from the `start_index`).  The leaf nodes display the final subsets (e.g., `[1, 1]`, `[1, 2]`, `[1, 3]`, etc.).  Each leaf node is labeled with the sum of its elements; those summing to 4 are marked in green (`sum == 4`), while those exceeding 4 are marked in red (`sum > 4`).  The arrows indicate the flow of the algorithm, showing how subsets are built recursively.  The gray arrows represent paths that are not explored further because they exceed the target sum.](images/image-14-04-5-EW2B7EF5.svg)

Initially, for the root combination, `start_index` is set to 0. As we recursively build each combination, `start_index` is updated to the index of the current element being added. By doing this, we ensure that in the next recursive call, we only consider elements from the updated index onward in the input array.

This maintains the required order and prevents duplicates because we never revisit previous elements. Since each combination is built by only adding elements that come after the current element in the input array, we avoid generating the same combination in a different order.

Try it yourself

Write your solution to the problem before checking the reference implementation.

[Open Code Editor](/exercises/coding-patterns/backtracking/combinations-of-a-sum)

## Implementation

In our algorithm, the termination condition requires us to know the sum of the current combination. While we could use a separate variable to track the sum of each combination, this isn't necessary. Instead, we can repurpose our target value. **When we choose a number to a combination, we reduce the target value by that number**. This way, the target value dynamically tracks the remaining sum needed to reach the original target. We see how this works below, where the target gets reduced by the value we add to the combination:

![Image represents a decision tree illustrating a recursive process, possibly for finding a subset of numbers that sums to a target value.  The root node shows an empty array `[]` with a `target` value of 4.  Three branches emanate from this root, each labeled with 'choose' followed by a number (1, 2, or 3), representing the selection of an element (implicitly from a larger set not shown). Each branch leads to a child node.  These child nodes display an array containing the chosen element (e.g., `[1]`, `[2]`, `[3]`) and an updated `target` value, calculated by subtracting the chosen element from the previous target (e.g., 4-1=3, 4-2=2, 4-3=1).  The updated `target` value suggests a recursive continuation of the process, where the algorithm would continue to choose elements until the target becomes zero, implying a solution has been found, or becomes negative, indicating no solution exists with the chosen path.  The structure visually depicts the exploration of different solution paths through recursive choices.](images/image-14-04-6-ME2YMGPF.svg)

This means that when we reach a target of 0, we've found a valid combination. If the target becomes negative, we can terminate the current branch of the search:

![Image represents a decision tree illustrating a recursive algorithm, likely for finding combinations that sum to a target value.  The root node is `[]`, target = 4, representing an empty initial set and a target sum of 4.  From this root, three branches descend, labeled 1, 2, and 3, representing the addition of those numbers to the set. Each subsequent node shows the current set (e.g., `[1,1]`) and the remaining target value (e.g., `target = 3-1 = 2`), calculated by subtracting the added number from the previous target.  The tree continues recursively until the target becomes 0 (e.g., `[1,3]`, `[2,2]`), at which point a green arrow indicates that the combination is added to the result and the branch terminates.  If the target becomes negative (e.g., `[2,3]`, `[3,3]`), a red arrow points to 'stop,' signifying that this branch does not yield a solution.  The orange numbers on the branches indicate the number being added at each step.  The algorithm explores all possible combinations by systematically adding numbers from 1 to 3 until either the target is reached or it becomes negative.](images/image-14-04-7-76N3G6QM.svg)

Python

JavaScript

Java

```
from typing import List
    
def combinations_of_sum_k(nums: List[int], target: int) -> List[List[int]]:
    res = []
    dfs([], 0, nums, target, res)
    return res
    
def dfs(combination: List[int], start_index: int, nums: List[int], target: int,
        res: List[List[int]]) -> None:
    # Termination condition: If the target is equal to 0, we found a combination
    # that sums to 'k'.
    if target == 0:
        res.append(combination[:])
        return
    # Termination condition: If the target is less than 0, no more valid
    # combinations can be created by adding it to the current combination.
    if target < 0:
        return
    # Starting from start_index, explore all combinations after adding nums[i].
    for i in range(start_index, len(nums)):
        # Add the current number to create a new combination.
        combination.append(nums[i])
        # Recursively explore all paths that branch from this new combination.
        dfs(combination, i, nums, target - nums[i], res)
        # Backtrack by removing the number we just added.
        combination.pop()
```

![](images/copy.3248da0c.svg)

### Complexity Analysis

**Time complexity:** The time complexity of `combinations_of_sum_k` is O(ntarget/m)O(n^{target/m})O(ntarget/m), where nnn denotes the length of the array, and mmm denotes the smallest candidate. This is because, in the worst case, we always add the smallest candidate mmm to our combination. The recursion tree will branch down until the sum of the smallest candidates reaches or exceeds the target. This results in a tree depth of target/mtarget/mtarget/m. Since the function makes a recursive call for up to nnn candidates at each level of the recursion, the branching factor is nnn, giving us the time complexity of O(ntarget/m)O(n^{target/m})O(ntarget/m).

**Space complexity:** The space complexity is O(target/m)O(target/m)O(target/m), which includes:

* The recursive call stack depth, which is at most target/mtarget/mtarget/m in depth.
* The combination list can also require at most O(target/m)O(target/m)O(target/m) space since the longest combination would consist of the smallest element mmm repeated target/mtarget/mtarget/m times.