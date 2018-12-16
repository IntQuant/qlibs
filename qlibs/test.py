class A():
    def t(self):
        print("A")

class B():
    def t(self):
        print("B-t")
    def p(self):
        print("B-p")

class C(A, B):
    def t(self):
        super(A, self).t()
        super().p()
        
C().t()
