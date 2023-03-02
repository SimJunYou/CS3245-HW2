list1 = [1, 2, 6, 7, 9, 10, 52, 61, 838, 1000, 12302]
list2 = [4, 8, 34, 46, 88, 112]
ptr1 = ptr2 = 0
output = []
while ptr1 < len(list1) and ptr2 < len(list2):
    val1, val2 = list1[ptr1], list2[ptr2]
    if val1 == val2:
        output.append(val1)
        ptr1 += 1
        ptr2 += 1
    elif val1 > val2:
        output.append(val2)
        ptr2 += 1
    else:
        output.append(val1)
        ptr1 += 1

while ptr1 < len(list1):
    output.append(list1[ptr1])
    ptr1 += 1
while ptr2 < len(list2):
    output.append(list2[ptr2])
    ptr2 += 1

print(output)
print(sorted(list(set([*list1, *list2]))))
