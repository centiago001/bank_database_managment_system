import mysql.connector as sql

class Database:
    def createdatabase(self):
        conn=sql.connect(user=self.userid,password=self.pwd)
        cur=conn.cursor()
        cur.execute("create database projbankdb")
        msql="create table projbankdb.accmaster (accno integer primary key auto_increment,name varchar(25), balance integer)AUTO_INCREMENT=1000"
        cur=conn.cursor()
        cur.execute(msql)
        msql="create table projbankdb.trans(tid integer primary key auto_increment , accno integer references projbankdb.accmaster(accno),ttype enum('w','d'),amount integer, tdate TIMESTAMP DEFAULT NOW())" 
        cur=conn.cursor()
        cur.execute(msql)
        conn.close()
        print("Database Created...")

    def checkdatabase(self):
        conn=sql.connect(user=self.userid,password=self.pwd)
        cur=conn.cursor()
        cur.execute("show databases")
        lst=cur.fetchall()
        for rec in lst:
            if rec[0]=="projbankdb":
                break
        else:
            self.createdatabase()
            
    def __init__(self):
        self.userid="root"
        self.pwd="admin"
        try:
            self.checkdatabase()
            self.conn=sql.connect(user=self.userid,password=self.pwd,database="projbankdb")   
        except Exception as er:
            print("ERROR:",er)

    def openAcc(self,nm,bl):
        msql="insert into accmaster(name,balance) values(%s,%s)"
        cur=self.conn.cursor()
        cur.execute(msql,[nm,bl])
        msql="select max(accno) from accmaster"
        cur=self.conn.cursor()
        cur.execute(msql)
        row=cur.fetchone()
        self.addTrans(row[0],'d',bl)
        self.conn.commit()
        return row[0]

    def search(self,an):
        msql="select * from accmaster where accno=%s"
        cur=self.conn.cursor()
        cur.execute(msql,[an])
        row=cur.fetchone()
        return row
    
    def deposit(self,an,amt):
        msql="update accmaster set balance=balance+%s where accno=%s"
        cur=self.conn.cursor()
        cur.execute(msql,[amt,an])
        self.addTrans(an,"d",amt)
        self.conn.commit()

    def withdraw(self,an,amt):
        row=self.search(an)
        if int(row[2])>=int(amt):
            msql="update accmaster set balance=balance-%s where accno=%s"
            cur=self.conn.cursor()
            cur.execute(msql,[amt,an])
            self.addTrans(an,"w",amt)
            self.conn.commit()
            return True
        return False

    def list(self):
        cur=self.conn.cursor()
        cur.execute("select * from accmaster")
        lst=cur.fetchall()
        return lst

    def closeAcc(self,an):
        cur=self.conn.cursor()
        cur.execute("delete from trans where accno=%s",[an])
        cur=self.conn.cursor()
        cur.execute("delete from accmaster where accno=%s",[an])
        self.conn.commit()

    def getTrans(self,an):
        msql="select ttype,amount,tdate from trans where accno=%s"
        cur=self.conn.cursor()
        cur.execute(msql,[an])
        lst=cur.fetchall()
        return lst
        
    def addTrans(self,an,ttype,amt):
        msql="insert into trans(accno,ttype,amount)  values(%s,%s,%s)"
        cur=self.conn.cursor()
        cur.execute(msql,[an,ttype,amt])
        
        
bankdb=Database()
while True:
    menu="1:New Account\n2:Deposit\n3:Withdraw\n4:List\n5:Search\n6:Close Acc\n7:Statement\n8:Exit"
    print("-"*15)
    print(menu)
    ch=int(input("Enter Choice:"))
    print("-"*15)
    if ch==8:
        break
    if ch==1:
        nm=input("Enter Name:")
        bl=input("Enter Opening Bal:")
        an=bankdb.openAcc(nm,bl)
        print("Account Opened AccNo :",an)
    if ch==2:
        an=input("Enter AccNo:")
        amt=input("Enter Amount to Deposit:")
        if bankdb.search(an)==None:
            print("AccNo Not Found..")
        else:
            bankdb.deposit(an,amt)
            print("Amount Deposited..")

    if ch==3:
        an=input("Enter AccNo:")
        amt=input("Enter Amount to Withdraw:")
        if bankdb.search(an)==None:
            print("AccNo Not Found..")
        else:
            if bankdb.withdraw(an,amt):
                print("Amount Withdrawn..")
            else:
                print("Insufficient Balance:")
    if ch==4:
        lst=bankdb.list()
        print("="*38)
        print("AccNo","Name".ljust(22),"Balance")
        print("-"*38)
        for rec in lst:
            print(rec[0],rec[1].ljust(20),str(rec[2]).rjust(8))
        print("="*38)
    if ch==5:
        an=input("Enter AccNo:")
        row=bankdb.search(an)
        if row==None:
            print("AccNo Not Found..")
        else:
            print("Name:",row[1])
            print("Bal :",row[2])
        
    if ch==6:
        an=input("Enter AccNo:")
        row=bankdb.search(an)
        if row==None:
            print("AccNo Not Found..")
        else:
            print("Name:",row[1])
            print("Bal :",row[2])
            ans=input("Are You Sure ?(y/n):")
            if ans in "Yy":
                bankdb.closeAcc(an)
                print("Account Closed...")

    if ch==7:
        an=input("Enter AccNo:")
        row=bankdb.search(an)
        if row==None:
            print("AccNo Not Found..")
        else:
            print("Name:",row[1])
            print("Bal :",row[2])
            lst=bankdb.getTrans(an)
            print("="*40)
            print("Date".ljust(15),"Deposit".ljust(10),"Withdraw".ljust(10))
            print("="*40)
            for rec in lst:
                print(rec[2].strftime("%d-%m-%Y"),str(rec[1]).rjust(10) if rec[0]=="d"  else str(rec[1]).rjust(24))
            print("="*40)
