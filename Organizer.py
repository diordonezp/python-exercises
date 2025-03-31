import calendar
import datetime
import numpy as np
import matplotlib.pyplot as plt
import random as rd
from openpyxl import load_workbook

# Class organizer-------------------------------------------------------------------------------------------------------------------------------------
class Organizer:
    """The organizer is called to generate a directory of the accounts and arrange the money. To initialize, Organizer needs an accounts list
    of the form:
    accounts=[[account 1 name,account 1 key],
              [account 2 name,account 2 key],
              ...
              [account N name,account N key]]
    where the keys are 1 letter assigments to the accounts."""

    def __init__(self,accounts):
        """Constructor: generates accounts_PG, a private directory of the accounts and attach an 2D float_vector with budgets
        and bills to each account. Aditionally it creates names, constbills, dailybills, and savings directories to store any constant,
        daily bills or savings."""
#       Default commands.
        self.__command_letters=['P','G','T','A','d']
#       Definitions.
        self.__names={}
        self.__accounts_PG={}
        self.__constbills={}
        self.__dailybills={}
        self.__savings={}
        for i in accounts:
#           Takes care that the keys asigned to each account aren't used by the commands.
            if i[1] in self.__command_letters: raise TypeError(f'{self.__command_letters} Not allowed key.')
#           Takes care that the keys are a char: one length string.
            if len(i[1])>1: raise TypeError("Key must be one letter.")
#           Takes care that the account keys aren't repeated.
            if i[1] in self.__accounts_PG: raise TypeError(f'{i[1]} Key already used for another account.')
#           Store the account dictionary: index 0 for budget and 1 index for bill.
            self.__accounts_PG[i[1]]=[0.0,0.0]
#           Store the names dictionary.
            self.__names[i[1]]=i[0]
#       Store the days for the 'd' command.
        self.__days=0

    def set_constbill(self,account,constbill,command_letter=""):
        """In case an account has a constant payment, this function assigns to the account dictionary a list that will contain
        the amount of the bill and the times it has been pay and the value of the pay. Additionally, it creates constbill
        directory with the command letter and the attached account for this bill."""
#       By default, the command letter asigned to the constbill will be te lowcase of the account key.
        if command_letter=="":
            command_letter=account.lower()
#       Take cares that the new constbill command is already used by the command letters or the account keys.
        if command_letter in self.__command_letters or command_letter in self.__accounts_PG:
            raise TypeError(f'{command_letter} key already used.')
#       The command used must be one letter length.
        if len(command_letter)>1: raise TypeError("Command must be one letter.")
        else:
#           Attach the command to the command letters list.
            self.__command_letters.append(command_letter)
#           Appends the cosntant bill to the accounts dictionary.
            self.__accounts_PG[account].append([0,constbill])
#           Creates the constbill directory that relates the new commando with the respective account, and the postition of this
#           new array in the accounts directory.
            self.__constbills[command_letter]=[account,len(self.__accounts_PG[account])-1]

    def set_dailybill(self,account,dailybill,):
        """In case an account has a daily payment, this function assigns to the dailybills directory a list that will contain
        the amount of the daily bill and a boolean for unique payment. If there are more than one daily pay in one account, the
        payments are added up."""
#       Checks that the account is in the directory.
        if account not in self.__accounts_PG: raise TypeError(f'{account} not an account.')
        if account in self.__dailybills:
#           If the account has already a daily bill, the new bill is added up.
            self.__dailybills[account][0]+=dailybill
        else:
#           Attach the list to the directory: index 0 for the amount of the daily bill and index 1 for uniquepay boolean.
            self.__dailybills[account]=[dailybill,False]

    def set_savingaccount(self,account):
        """In case the account has some savings to put appart from paying money, this function assings to the savings directory
        the name of the account and the space to store this savings."""
#       Checks that the account is in the directory.
        if account not in self.__accounts_PG: raise TypeError(f'{account} not an account.')
        if account in self.__dailybills and self.__dailybills[account][1]==True:
#           If the account is for unique pay, it cannot has savings.
            raise TypeError(f'{account} cannot has savings since is a unique payment account.')
        else:
#           Attach the account to the savings directory.
            self.__savings[account]=0.0

    def set_uniquepay(self,account):
        """In case an account with a daily payment is set to pay only for this bill, this function set the daily bill directory
        list boolean ti true."""
#       Checks that the account is in daily bills.
        if account in self.__dailybills:
#           If the account is in savings, it cannot has a unique payment atribute.
            if account in self.__savings:
                raise TypeError(f'{account} cannot be set to unique payment since it has savings.')
#           Sets the boolean to true.
            self.__dailybills[account][1]=True
        else: raise TypeError(f'{account} must have a daily bill.')

    def set_mode(self,line,index):
        """This function takes in a line from the daily bills txt and return a list
        [command mode,account for the command action]"""
        mode=[]
#       Checks that the line is not empty.
        if line=='': raise TypeError(f'Line {index+1}: empty mode.')

#       Checks the first letter of the line to be a command and append the command index to mode.
        if line[0] in self.__command_letters: mode.append(self.__command_letters.index(line[0]))
        else: raise TypeError(f'Line {index+1}: first character must be a command character.')

#       Appends the rest of the command to mode.
        mode.append(line[1:])

#       For modes P or G
        if mode[0]==0 or mode[0]==1:
#           If the length is 1, checks that the account is in the accounts list
            if len(mode[1])==1:
                if mode[1] not in self.__names: raise TypeError(f'Line {index+1}: {mode[1]} not an account key.')
#           If the lenght is grater than 1, it means is refering to a saving account. It checks that the saving key is used.
            elif len(mode[1])>1:
                if mode[1][0]!='A':
                    raise TypeError(f'Line {index+1}: command must have one account entry or specify A key for savings.')
                if mode[1][1:] not in self.__savings: raise TypeError(f'Line {index+1}: {mode[1][1:]} not a savings account key.')
            elif len(mode[1])==0:
                raise TypeError(f'Line {index+1}: No account especified.')
#           If not error is detected, function returns the mode
            return mode

#       For mode T
        elif mode[0]==2:
#           If the line doesn't have a dash line, returns an error.
            if '-' not in mode[1] or len(mode[1])<3: raise TypeError(f'Line {index+1}: {line} command invalid.')

#           If the transaction is made from a normal account, it checks that the dashed line is in position 1.
            elif mode[1][1]=='-':
#               Checks that the first account is on the accounts list.
                if mode[1][0] not in self.__names:
                    raise TypeError(f'Line {index+1}: {mode[1][0]} not an account.')
                if mode[1][2:] not in self.__names:
#                   If the length of the account is 1, it means that the account is wrong.
                    if len(mode[1][2:])==1:
                        raise TypeError(f'Line {index+1}: {mode[1][2:]} not an account.')
                    else:
#                       For the seccond account if is not in the accounts list, checks that the saving key is active.
                        if mode[1][2]!='A': raise TypeError(f'Line {index+1}: {mode[1][2:]} has no saving atribute A.')
#                       Then, it checks that the account is in the savings accounts list.
                        if mode[1][3:] not in self.__savings: raise TypeError(f'Line {index+1}: {mode[1][3:]} not a savings account.')

#               If none of the errors are spotted, function returns the mode: [2,account 1,account 2].
                mode[1]=line[1]
                mode.append(line[3:])
                return mode

#           If the transaction is made from a savings account, it checks that the dashed line is in position 2.
            elif mode[1][2]=='-':
#               Checks that the first character is the A saving key
                if mode[1][0]!='A':
                    raise TypeError(f'Line {index+1}: {mode[1][0:2]} has no saving atribute A.')
#               Checks that the first account is on the accounts list.
                if mode[1][1] not in self.__savings:
                    raise TypeError(f'Line {index+1}: {mode[1][1]} not a savings account.')
                if mode[1][3:] not in self.__names:
#                   If the length of the account is 1, it means that the account is wrong.
                    if len(mode[1][3:])==1:
                        raise TypeError(f'Line {index+1}: {mode[1][3:]} not an account.')
                    else:
#                       For the seccond account if is not in the accounts list, checks that the saving key is active.
                        if mode[1][3]!='A': raise TypeError(f'Line {index+1}: {mode[1][3:]} has no saving atribute A')
#                       Then, it checks that the account is in the accounts list.
                        if mode[1][4:] not in self.__savings: raise TypeError(f'Line {index+1}: {mode[1][4:]} not an account.')

#               If none of the errors are spotted, function returns the mode: [2,account 1,account 2].
                mode[1]=line[1:3]
                mode.append(line[4:])
                return mode

#           If none of the above is taken, it means that the line is wrong.
            else: raise TypeError(f'Line {index+1}: {line} command invalid.')

#       For mode d or any new command attached by the user:
        elif mode[0]>=4:
#           Checks that the rest of the line is a number. If it is a number, converts it in float.
            if len(line)>1:
                if not is_float(line[1:]):
                    raise TypeError(f'line {index+1}: {line[1:]} must be a number.')
                else:
                    mode[1]=float(line[1:])

#           If only the command is called, set the number as 1 by default.
            elif len(line)==1:
                mode[1]=1.0

            return mode

#       If none of the aboved is taken, an error is spotted, since the line does not match any command.
        else:
            raise TypeError(f'Line {index+1}: {line} command invalid.')

    def read_mode(self,mode,x,index):
        """reads the command mode and upload the account directory based on the txt info"""
#       If the mode is empty, it returns an error foe empty mode.
        if mode==[]: raise TypeError(f'Line {index+1}: The mode is empty. This line or a former line needs to set the mode.')

#       For P and G modes:
        if mode[0]==0 or mode[0]==1:
#           If the account is normal, then the amount is attached to the accounts dictionary.
            if len(mode[1])==1:
                self.__accounts_PG[mode[1]][mode[0]]+=float(x)
#           If the account is a saving account, the amount is store or subtract from savings dictionary.
            else:
                if mode[0]==0:
                    self.__savings[mode[1][-1]]+=float(x)
#               When substracting from the saving account, it also adds this amount to the profit and bill of the account, so this amount 
#               is also counted on the total proofit.
                if mode[0]==1:
                    self.__savings[mode[1][-1]]-=float(x)
                    self.__accounts_PG[mode[1][-1]][0]+=float(x)
                    self.__accounts_PG[mode[1][-1]][1]+=float(x)

#       For T mode:
        elif mode[0]==2:
#           If both accounts are normal, it subtracts the budget for the first account and adds it to the second account budget.
            if len(mode[1])==1 and len(mode[2])==1:
                self.__accounts_PG[mode[1]][0]-=float(x)
                self.__accounts_PG[mode[2]][0]+=float(x)

#           If the first account is normal and the second is savings, it substracts the amount from the normal account and adds it to the savings 
#           account.
            if len(mode[1])==1 and len(mode[2])!=1:
                self.__accounts_PG[mode[1]][0]-=float(x)
                self.__savings[mode[2][-1]]+=float(x)

#           If the first account is saving and the second is normal, it substracts the amount from the saving account and adds it to the savings 
#           account.
            if len(mode[1])!=1 and len(mode[2])==1:
                self.__savings[mode[1][-1]]-=float(x)
                self.__accounts_PG[mode[2]][0]+=float(x)

#           If both accounts are saving, it substracts the amount from the first saving account and adds it to the second savings account.
            if len(mode[1])!=1 and len(mode[2])!=1:
                self.__savings[mode[1][-1]]-=float(x)
                self.__savings[mode[2][-1]]+=float(x)

#       For d mode:
        elif mode[0]==4:
            self.__days+=mode[1]

#       For other modes: adds the amount of times the constant bill is paid.
        elif mode[0]>4:
            command=self.__command_letters[mode[0]]
            self.__accounts_PG[self.__constbills[command][0]][self.__constbills[command][1]][0]+=mode[1]

    def read(self,name,b_days=False):
        """Read a daily budget-bills .txt and puts the info in the respective 2D vector component."""
#       Sets the amounts to cero again, in case it is full from a recent call
        for i in self.__accounts_PG:
            self.__accounts_PG[i][0]=0.0
            self.__accounts_PG[i][1]=0.0

        for i in self.__constbills:
            self.__accounts_PG[self.__constbills[i][0]][self.__constbills[i][1]][0]=0

        for i in self.__savings:
            self.__savings[i]=0.0

        self.__days=0

        L=count_lines(name)
        f=open(name,"r")
        mode=[]

#       Runs over the lines of the txt.
        for i in range(L):
            x=f.readline().strip()
#           If the line contains a comment, the character '#' defines where the command line ends (command, or number).
            if '#' in x:
                x=x[:x.index('#')].strip(' ')
#           If the line is a number, reads the mode to asigne the value in the directory.
            if is_float(x):
                if mode[0]>=4:
                    raise TypeError(f'Line {i+1}: invalid mode before a number input -> {self.__command_letters[mode[0]]}.\n'
                                   f'Available modes are: {self.__command_letters[0:3]}.')
                else:
                    self.read_mode(mode,x,i)
#           If the line is empty, it pass to the next line.
            elif(x==''): pass
#           If the line is a command, it sets the mode, and read it.
            else:
                mode=self.set_mode(x,i)
                if mode[0]>=4:
                    self.read_mode(mode,x,i)

#       Set the month days.
        month_days=mdays()

#       Checks that the days are not grater than the month days.
        if self.__days>month_days: raise TypeError("Number of days cannot be longer that the month days.")
        if int(self.__days)!=datetime.datetime.now().day:
            print('\x1b[31mWARNING:\x1b[0m'+f'Los días intriducidos ({int(self.__days)}) no coinciden con la fecha actual '
                                            f'({datetime.datetime.now().day}).')
#       Total variables are set to store the total budget, bill and proyection.
        total_budget=0
        total_bill=0
        total_savings=0
        total_proyection=0

#       Shows the upload accounts, and predicts how much can be extra spent (besite daily bills) for each account.
        print(f'Dias: {int(self.__days)} de {month_days}\n')

        for i in self.__accounts_PG:
#           Account bill is a local variable to store the total bill: spent by constant and non constnat payments
            account_bill=self.__accounts_PG[i][1]
#           If the directoy item length is grater than 2, it means it has constant bills that are store
            if len(self.__accounts_PG[i])>2:
                 for j in range(2,len(self.__accounts_PG[i])):
                    account_bill+=self.__accounts_PG[i][j][0]*self.__accounts_PG[i][j][1]

#           Stores the account budget and bill in total variables.
            total_budget+=self.__accounts_PG[i][0]
            total_bill+=account_bill

#           If the account is saving, it adds the amount to total savings.
            if i in self.__savings:
              total_savings+=self.__savings[i]

#           Account proyection is a local variable to calculate the account daily proyection bill for the month. It is only
#           activate if the days passed are less than the month:
            if(month_days>self.__days):
#               This proyection starts as the account budget minus the account total bill, divided by the remaining days.
                account_proyection=(self.__accounts_PG[i][0]-account_bill)/(month_days-self.__days)
#               The proyection is added up to the total proyection.
                total_proyection+=account_proyection

                if i in self.__dailybills:
#                   If there is a daily bill with unique pay for the account, the proyection stores what is left to fill the
#                   the month bill.
                    if self.__dailybills[i][1]:
#                       If b_days==True, the proyection is made with the bussines days only.
                        if b_days:
                            Bdays=bdays()
                            Bdays_till=bdays_til(int(self.__days))
#                           Bussines days proyection, a auxiliar variable
                            Baccount_proyection=(self.__accounts_PG[i][0]-account_bill)/(Bdays-Bdays_till)
    
#                           If the account is for unique payment, and the proyection is positive, meaning that there is extra
#                           charge in the account, it is substracted from the total proyection.
                            if Baccount_proyection-self.__dailybills[i][0]>0:
                                total_proyection-=account_proyection
#                           Insetad, if the proyection is negative, meaning that there is not enough money to fulfill the daily
#                           bill, it is subtracted from the total proyection, taking care that the subtracted is distributed over
#                           all days of the month.
                            else:
                                total_proyection-=account_proyection-(Baccount_proyection-self.__dailybills[i][0])*(Bdays-Bdays_till)/(month_days-self.__days)
                            
#                           Finally, account_proyection stores what what is needed to fill the
#                           the month bill (negative amount), or the extracharge (positive amount).
                            account_proyection*=(month_days-self.__days)
                            account_proyection-=(Bdays-Bdays_till)*self.__dailybills[i][0]
                                
#                       If b_days==False, the proyection is made with the whole days of the month.
                        else:
#                           If the account is for unique payment, and the proyection is positive, meaning that there is extra
#                           charge in the account, it is substracted from the total proyection.
                            if account_proyection-self.__dailybills[i][0]>0:
                                total_proyection-=account_proyection
#                           Insetad, if the proyection is negative, meaning that there is not enough money to fulfill the daily
#                           bill, it is subtracted from the total proyection.
                            else:
                                total_proyection-=self.__dailybills[i][0]

#                           Finally, account_proyection stores what what is needed to fill the
#                           the month bill (negative amount), or the extracharge (positive amount).
                            account_proyection*=(month_days-self.__days)
                            account_proyection-=(month_days-self.__days)*self.__dailybills[i][0]
        
#                   If there is a daily bill without unique pay for the account, the proyection substracs the daily payment. 
                    else:
#                       If b_days==True, the proyection is made with the bussines days only.
                        if b_days:
                            Bdays=bdays()
                            Bdays_till=bdays_til(int(self.__days))
#                           Bussines days proyection, a auxiliar variable
                            Baccount_proyection=(self.__accounts_PG[i][0]-account_bill)/(Bdays-Bdays_till)
                            
#                           Total_proyection stores the usual proyection, even if it's negative.
                            total_proyection-=account_proyection-(Baccount_proyection-self.__dailybills[i][0])*(Bdays-Bdays_till)/(month_days-self.__days)
                            
#                           Account_proyection stores the usual proyection, even if it's negative, taking care that the proyection is
#                           over all the days of the month.
                            account_proyection=(Baccount_proyection-self.__dailybills[i][0])*(Bdays-Bdays_till)/(month_days-self.__days)
                        
#                       If b_days==False, the proyection is made with the whole days of the month, just substracting the daily
#                       bill.
                        else:
                            account_proyection-=self.__dailybills[i][0]
                            total_proyection-=self.__dailybills[i][0]


#           Each account is printed with the name, budget, bill, actual budget and proyection, depending on the daily bill and
#           unique payment state of the account, and the number of days passed.
            print("|","-"*100,"|")
            print("Cuenta:",self.__names[i])
#           If the account has saving atrivute, the budget will be the profit plus the savings.
            if i in self.__savings:
                print("Ingresos:",self.__accounts_PG[i][0]+self.__savings[i])
            else:
                print("Ingresos:",self.__accounts_PG[i][0])
            print("Gastos:",account_bill)
            print("Presupuesto actual:",self.__accounts_PG[i][0]-account_bill)
#           If the account is saving, prints the savings.
            if i in self.__savings:
                print(f'Ahorro: {self.__savings[i]}\n')
            else: print('\n')
            if(month_days>self.__days):
                if i in self.__dailybills:
                    if self.__dailybills[i][1] and account_proyection<0:
                        print("Cargo necesario para completar la cuota mensual:",-account_proyection,"\n")
                    elif self.__dailybills[i][1] and account_proyection>=0:
                        print("Cargo excedente en la cuenta:",account_proyection,"\n")
                    elif not self.__dailybills[i][1]:
                        print("Proyección de máximo gasto extra por día:",account_proyection,"\n")
                else:
                    print("Proyección de máximo gasto extra por día:",account_proyection,"\n")

#       Now it prints the total amounts.
        print()
        print("|","-"*100,"|")
        print("Ingresos totales:",total_budget+total_savings)
        print("Gastos Totales:",total_bill)
        print("Presupuesto actual total:",total_budget-total_bill)
        print(f'Ahorro total: {total_savings}\n')
        if(month_days!=self.__days):
            print("Proyección de máximo gasto total extra por día:",total_proyection,"\n")
            
            
    def save_to_excel(self,name):
        """A function to store the budget-bill-savings for every account as an existing excel."""
#       checks that the days and month are correct.
        if mdays()>self.__days:
            ans=input(f'Number of days:{self.__days} is less than the month, do you want to storage incomplete month data? (y/n)\n')
            if ans=='n':
                return 'Terminated'
            elif ans!='y':
                raise TypeError(f'{ans} not a valid answer.')
            
        months=['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        
        d_year=datetime.datetime.now().year
        year=input(f'Default year is set to {d_year}. Want to change the year? (y/n)\n')
        if year=='y':
            year=input(f'Enter year:')
        elif year=='n':
            year=d_year
        else:
            raise TypeError(f'{month} not a valid answer.')
            
        d_month=months[datetime.datetime.now().month-1]
        month=input(f'Default month is set to {d_month}. Want to change the month? (y/n)\n')
        if month=='y':
            month=input(f'Enter month:')
            if month not in months:
                while month not in months:
                    month=input(f'{month} not a month or misspelled. Enter a valid month:{months}')
        elif month=='n':
            month=d_month
        else:
            raise TypeError(f'{month} not a valid answer.')
            
#       Reads the existing .xlsx file.
        wb=load_workbook(name)
        work_sheet=wb['Datos']
                    
        for i in self.__savings:
#           Account budget is a local variable to store the account budget: Entry payments and savings.
            account_budget=self.__accounts_PG[i][0]
            account_budget+=self.__savings[i]
#           Account bill is a local variable to store the account bill: spent by constant and non constnat payments.
            account_bill=self.__accounts_PG[i][1]
#           If the directoy item length is grater than 2, it means it has constant bills that are store.
            if len(self.__accounts_PG[i])>2:
                 for j in range(2,len(self.__accounts_PG[i])):
                    account_bill+=self.__accounts_PG[i][j][0]*self.__accounts_PG[i][j][1]
#           Savings is a variable to store the savings left at the end of the month.
            account_savings=account_budget-account_bill
#           Appends the new row with budget-bill-savings, year and month info.
            work_sheet.append([year,month,self.__names[i],account_budget,account_bill,account_savings])
#       Saves the excel.
        wb.save(name)
        
        return f'File save with name {name}.'

    def show_dict(self):
        """a funtion to print the dictionaries: accounts, account names, constbills and daily bills."""
        print("Accounts: ",self.__accounts_PG)
        print(f'Account names: {self.__names}')
        print("Constant Bills: ",self.__constbills)
        print("Daily Bills: ",self.__dailybills)
        print("Savings: ",self.__savings)

    def show_commands(self):
        """a funtion to print the account names and commands."""
        print(self.__command_letters)

    def rules(self):
        """a function to print the rules of the commands to build the txt info"""
        print("-"*50,"FILE RULES","-"*50,"\n"
             "File sintax: budget-savings-bill txt must be written following the sintax\n\n"
             "1. Command line: first letter for the command defines the action and the rest of the command"
              " specifies account and details\n"
             "2. Value associated with the command\n\n"
             "Commands:\n"
             "P[]: use to charge the account [] a budget.\n"
             "G[]: use to charge the account [] a bill.\n"
             "T[1]-[2]: use to change a budget from [1] to [2]. [1] or [2] can be either accounts or saving accounts.\n"
             'A[]: used to specify if the amount is attached to the savings atribute of [].\n'
             "d[n]: use to set [n] new days (n=1 by default).")
        
        if len(self.__command_letters)>5:
            for i in self.__command_letters[5:]:
                print(f"{i}[n]: use to set [n] constant bills for the {self.__constbills[i][0]} account (n=1 by default).")
        print('\nThe character \'#\' can be used to put comments about the budgets of bills.\n')
        print("\nExample:\n")
        names=self.__names
        com=self.__command_letters
        com_1=com[:3]
        com_2=com[5:]

        for i in range(3):
            l=list(names)
            rd.shuffle(com_1)
            print('d',end='')
            prob_print(int(rd.uniform(2,5)),50)
            print()
            if len(com_2)>0:
                print(f'{com_2[0]}{int(rd.uniform(2,10))}')
            for j in range(3):
                rd.shuffle(l)
                rd.shuffle(com_2)
                if com_1[j]=='T' and len(l)>1:
                    print(f'{com_1[j]}{l[0]}-',end='')
                    prob_print('A',45)
                    print(f'{l[1]}\n{int(rd.uniform(0,10000))*50}',end='')
                    if int(rd.uniform(0,10))<3:
                        print(' # Transaction description')
                    else:
                        print()
                elif com_1[j]!='T':
                    print(f'{com_1[j]}',end='')
                    prob_print('A',45)
                    print(f'{l[0]}\n{int(rd.uniform(0,10000))*50}',end='')
                    if int(rd.uniform(0,10))<3:
                        if com_1[j]=='P':
                            print(' # Budget description')
                        elif com_1[j]=='G':
                            print(' # Bill description')
                    else:
                        print()
            print()


    
# funciones globales------------------------------------------------------------------------------------------------------------
def count_lines(name):
    """Function that gives the leng of a .txt in lines."""
    f=open(name,"r")
    x=f.readlines()
    f.close()
    return len(x)

def is_float(x):
    """Function that gives a boolean for float numbers."""
    try:
        float(x)
        return True
    except ValueError:
        return False

def mdays():
    """Function that gives the days of the actual month."""
    now = datetime.datetime.now()
    return calendar.monthrange(now.year, now.month)[1]

def bdays():
    """Function that gives the bussines days of the actual month."""
    now=datetime.datetime.now()
    cal=calendar.Calendar()
    return len([x for x in cal.itermonthdays2(now.year,now.month) if x[0] !=0 and x[1] < 5])

def bdays_til(day):
    """Function that gives the bussines days until a especific day of the actual month."""
    if day==0:
        return 0
    else:
        now = datetime.datetime.now()
        year=str(now.year)
        month=str(now.month)
        if len(month)==1:
            month='0'+month
        aux_day=str(day)
        if len(aux_day)==1:
            aux_day='0'+aux_day
        lastday=lambda x: 1 if np.is_busday(x) else 0

        return np.busday_count(year+'-'+month,year+'-'+month+'-'+aux_day)+lastday(year+'-'+month+'-'+aux_day)

def prob_print(string,prob):
    """A function to print a string with certain probability P from 0 to 100"""
    if int(rd.uniform(0,100))<=prob:
        print(string,end='')
