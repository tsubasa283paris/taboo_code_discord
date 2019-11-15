class Abc:
    def __init__(self, v):
        self.value = v
    
    def double(self):
        return self.value * 2
    
    def getvalue(self):
        return self.value

list = [Abc(i) for i in range(5)]

for i in range(len(list)):
    print(list[i].double())

print("---")

for i, obj in enumerate(list):
    if obj.getvalue() == 2:
        list.pop(i)
    print(obj)
