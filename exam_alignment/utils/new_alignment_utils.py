def longest_increasing_subsequence_index(nums: list[int]):
    """
    获取一个列表中的最长递增子序列的索引。首先，它从主题列表中提取数字，然后找到最长的递增子序列，只返回开始位置在topics长度一半之前的。
     
    返回:
        list: 最长递增子序列的索引列表。
    """
    n = len(nums)
    dp = [[i] for i in range(n)]

    for i in range(n):
        for j in range(i):
            if nums[j][0] < nums[i][0]:
                if len(dp[j]) + 1 > len(dp[i]) or (len(dp[j]) + 1 == len(dp[i]) and dp[j][-1] == dp[i][-1] - 1):
                    dp[i] = dp[j] + [i]

    # We need to filter based on the original index, not the index in the nums list
    dp = list(filter(lambda lis:nums[lis[0]][1] < len(nums)/2, dp))
    dp = list(sorted(dp, key=lambda lis:len(lis), reverse=True))
    # Return the original indices, not the indices in the nums list
    return [nums[i][1] for i in dp[0]]