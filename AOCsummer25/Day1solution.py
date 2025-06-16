depths = [199,
200,
208,
210,
200,
207,
240,
269,
260,
263]
dc=0
uc=0
l = depths[0]
for n in depths[1:]:
    if n>l:
        dc+=1
    if n<l:
        uc+=1
    l=n
print("Number of times depth increases:",dc)
print("Number of times depth is less than the previous:",uc)