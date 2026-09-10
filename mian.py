from datetime import datetime

#获取当前时间
current_time =datetime.now()
print("Finally,I success to Commit and Publish Branch at" ,current_time);


#找2-100内的质数
#思路：质数是只能被1和它本身整除的数，2是唯一的偶数质数，所以从2开始循环，把能被2整除的数去掉。
#用变量nums=[]来存储质数，循环从2到100，判断每个数是否为质数，如果是就加入nums中。
nums=[]
for i in range(2,101) :#range不包含101
    is_prime=True #先假设i是质数
    for j in range(2,i):#判断i能否被比它更小的数整除，如果可以，i就不是质数
        if i%j==0:
            is_prime=False
            break
    if is_prime:
        nums.append(i) #把质数添加上去
print(nums)
