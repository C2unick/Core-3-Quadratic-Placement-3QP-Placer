import numpy
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
#Function computes the weight of all nets(fully-connected clique model):
def WeightFunction(New_net_matrix2,New_pad_matrix2):
    Weight=[0 for i in range(NumOfNets)]
    for i in range(NumOfNets):
        #count the gate names in this net(i+1)
        n=0
        for k in range(columns):
            if New_net_matrix2[i][k] != 0:
                n+=1
        #check if there is a fake pad connected to this net (i+1) or not
        NumOfFakePadsInThisNet=0
        for k in range(columns):#take every gate name in this net and compare it with all fake pads that you have
            if net_matrix[i][k] ==0:
                break
            for h in range(len(New_pad_matrix2)):
                if New_pad_matrix2[h][1]!=0:
                    break#because we became in real pad part of New_pad_matrix
                if net_matrix[i][k]==New_pad_matrix2[h][0]:                    
                        NumOfFakePadsInThisNet+=1 #if there is, then this net isn't a 2-point net
                        TwoPointNet=False
        #check if it connected to real pad or not
        ThisNetContainsRealPad=0
        for h in range(len(New_pad_matrix2)):
            if New_pad_matrix2[h][1]==i+1:
                ThisNetContainsRealPad=1    
                break
        n+=(NumOfFakePadsInThisNet+ThisNetContainsRealPad)
        if n<=1:
            Weight[i]=0#because we won't use this net
        else:
            Weight[i]=1/(n-1)       
    return Weight                        

#function returns the C, A, bx and by matrices 
def A_C_bx_by_Matrices(NumOfCurrentGates,gate_matrix1,net_matrix1,NumOfIDgatesInIDnet1,pad_matrix1,Weight4):
    A1=[[0 for i in range(NumOfCurrentGates)]for k in range(NumOfCurrentGates)]
    C1=[[0 for i in range(NumOfCurrentGates)]for k in range(NumOfCurrentGates)]
    bx1=[0 for i in range(NumOfCurrentGates)]
    by1=[0 for i in range(NumOfCurrentGates)]
    i=0
    net_name=0
    #save the gate names that function will build C and A matrices for(QP Input) in "IDGatesOfNewQPInput" array
    IDGatesOfNewQPInput=[0 for i in range(NumOfCurrentGates)]
    k=0
    for i in range(NumOfGates):
        if gate_matrix1[i][0]!=0:
            IDGatesOfNewQPInput[k]=i+1
            k+=1
    print("IDGatesOfNewQPInput:")
    print(IDGatesOfNewQPInput)
    #build c matrix
    for i in range(NumOfCurrentGates):
        CurrentGate=IDGatesOfNewQPInput[i]-1#"CurrentGate" var. represents the gate name that will be checked
        #get the net names that connected to this gate one at time 
        for k in range(columns):
            if gate_matrix1[CurrentGate][k] == 0:
                break#means that we finish the net names
            NetID=gate_matrix1[CurrentGate][k]-1                     
            #get all gate names in this net except the gate name that we work on it(CurrentGate+1)using net_matrix 
            for m in range(columns):
                if net_matrix[NetID][m]==0:
                    break    
                GateName1=net_matrix[NetID][m]
                if GateName1 != CurrentGate+1:
                    #search on the corrsponding name of gate with name "GateName1" in "IDGatesOfNewQPInput" array
                    WritePremission1=False
                    for g in range(NumOfCurrentGates):
                        if GateName1==IDGatesOfNewQPInput[g]:
                            corrs_name1=g
                            WritePremission1=True
                            break
                    # full this location based on the weight of the wire that connected "GateName1" and "CurrentGate+1" 
                    if  WritePremission1 :#k-point doesn't has a pad
                        if Weight4[NetID] == 0:
                            print("there is a problem,N:",NetID+1,"connects G:",GateName1,"to G:",CurrentGate+1)
                        C1[i][corrs_name1]+=Weight4[NetID]                
    #then, build A matrix from the C matrix..                     
    for i in range(NumOfCurrentGates):
        for k in range(NumOfCurrentGates):
            if i!=k: #full the non-digonal elements
                A1[i][k]=-1*C1[i][k]            
            if i==k: #full the digonal elements
                for h in range(NumOfCurrentGates):
                    A1[i][k]+=C1[i][h]            
    #add the(real and fake)pad weight to the digonal elements and build bx and by matrices...
    for i in range(len(pad_matrix1)):
        #check either it's a propagated gate or not
        if pad_matrix1[i][1] == 0: 
            gate_id=pad_matrix1[i][0]-1            
            for k in range(columns):#if it is, get every net name that connected to it at a time
                #notice that we use the original problem data not the arguments of this function, such that gate_matrix(not gate_matrix1)
                if gate_matrix[gate_id][k]==0:
                    break
                net_name=gate_matrix[gate_id][k]-1
                #get all gate names that connected to this pad,using net_matrix 
                for m in range(columns):
                    if net_matrix[net_name][m]==0:
                        break    
                    GateNameThatConnectedTopropagatedPad=net_matrix[net_name][m]
                    #search on the corrsponding name of gate with name "net_matrix[net_name][h]" in "IDGatesOfNewQPInput" array
                    WritePremission2=False
                    for g in range(NumOfCurrentGates):
                        if GateNameThatConnectedTopropagatedPad==IDGatesOfNewQPInput[g]:
                            corrs_name2=g
                            WritePremission2=True
                            break    
                    if  WritePremission2:#add the weight               
                        if Weight4[net_name] == 0:
                            print("there is a problem,N:",net_name+1,"connects Fake P:",pad_matrix1[i][0],"to G:",GateNameThatConnectedTopropagatedPad )
                        A1[corrs_name2][corrs_name2]+=Weight4[net_name]
                        bx1[corrs_name2]+=pad_matrix1[i][2]*Weight4[net_name]#multiply by the fake pad weight
                        by1[corrs_name2]+=pad_matrix1[i][3]*Weight4[net_name]              
        #if it is a real pad
        else:
            net_name=pad_matrix1[i][1]-1
            #get all gate names that connected to this pad,using net_matrix 
            for k in range(columns):
                if net_matrix[net_name][k]==0:
                    break    
                GateNameThatConnectedTorealPad=net_matrix[net_name][k]
                #search on the corrsponding name of gate with name "net_matrix[net_name][h]" in "IDGatesOfNewQPInput" array
                WritePremission2=False
                for g in range(NumOfCurrentGates):
                    if GateNameThatConnectedTorealPad==IDGatesOfNewQPInput[g]:
                        corrs_name2=g
                        WritePremission2=True
                        break    
                if  WritePremission2:                
                    if Weight4[net_name] == 0:
                        print("there is a problem,N:",net_name+1,"connects real P:",pad_matrix1[i][0],"to G:",GateNameThatConnectedTorealPad)
                    A1[corrs_name2][corrs_name2]+=Weight4[net_name]
                    bx1[corrs_name2]+=pad_matrix1[i][2]*Weight4[net_name]#multiply by the real pad weight
                    by1[corrs_name2]+=pad_matrix1[i][3]*Weight4[net_name]                      
    return A1,C1,bx1,by1,IDGatesOfNewQPInput;
                                  
#function sorts on x and return the ID of the gates that are on the LHS and the RHS in different matrices(assignment step):
def sortx(x,y):
    SingleKey=[0 for i in range(NumOfGates)]
    for i in range(NumOfGates):
        SingleKey[i]=1000000*x[i]+y[i]   
    sorted_SingleKey=sorted(SingleKey)
    sorted_IDs=[0 for i in range(NumOfGates)]
    GatePermission=[True for i in range(NumOfGates)]
    for i in range(NumOfGates):
        for k in range(NumOfGates):
            if sorted_SingleKey[i] == SingleKey[k]:
                if GatePermission[k]:
                    sorted_IDs[i]=k
                    GatePermission[k]=False
                    break    
    q=int(NumOfGates/2)
    LHS_IDgates=[sorted_IDs[i] for i in range(q)]#Put smaller number of gates on the left.
    RHS_IDgates=[sorted_IDs[k] for k in range(q,NumOfGates)]
    return LHS_IDgates,RHS_IDgates;
            
#function returns the 2 matrices with information about these gates which connect in different regions:
#first matrix(ConnectedGatesToLHS) contains the gate names, which are in RHS and connect to the gates in LHS,in this order: IDOfGateInLHS,IDOfGatesInRHS...
#second matrix(ConnectedGatesToRHS) is the opposite of the first matrix
def GatesConnectedInDifferentRegions(LHS_IDgates,RHS_IDgates):
    Region=["L","R"]
    for a in range(2):
        if Region[a]=="R":
            source=RHS_IDgates
            dest=LHS_IDgates
        elif Region[a]=="L" :
            source=LHS_IDgates
            dest=RHS_IDgates            
        #ConnectedGates matrix contains info. about connected gate in this order: IDOfGateInSource,IDOfGatesInDestination...
        ConnectedGates=[[0 for i in range (columns)] for k in range(len(source))]
        #determine the gates name in dest that connect to each gate in source 
        for i in range(len(source)): 
            #put the ID of the gate in source in the first col. in every row
            ConnectedGates[i][0]=source[i]+1
            m=1
            ExistedName=[False for q in range(len(dest))]
            #determine number of nets_that_will_be_checked and save it in "k"
            k=0
            while gate_matrix[source[i]][k]!=0:
                k+=1
            for h in range(k): 
                Net_NO=gate_matrix[source[i]][h]-1#check every net that in the gate_matrix row
                #check every the gate name, in the net_matrix row, either it in source or not
                for g in range(NumOfIDgatesInIDnet[Net_NO]): 
                    for v in range(len(dest)):
                        if net_matrix[Net_NO][g]==(dest[v]+1):#(+1)->because the id in dest array begin from 0 not 1
                            #check either the gate name "dest[v]+1" is already written or not 
                            if ExistedName[v] == False :
                                ConnectedGates[i][m]=dest[v]+1
                                m+=1
                                ExistedName[v]=True # index "v" is used
        if a==0:
            ConnectedGatesToLHS=ConnectedGates
        else:
            ConnectedGatesToRHS=ConnectedGates
    return ConnectedGatesToLHS,ConnectedGatesToRHS;                                   
#Propagate the gates and pads, that are connected and they are in different regions, to the center of the chip(x=50)(Containment step):
#the function returns the new pad matrix,that contains all info about the propagated gates and pads and the normal existing pads
def cont_step_for_LHS(ConnectedGatesToLHS):              
    #create fake_pad_matrix, but calculate the no. of rows first...
    row_fake_pad_matrix=0#"row_fake_pad_matrix" contains the no. of rows of the fake_pad_matrix            
    #to make sure that we won't count the same element more than one time        
    count_gate=[False for i in range(NumOfGates)]
    count_pad=[False for i in range(NumOfPads)]
    #count the gate names in "ConnectedGatesToLHS" array which will be propagated, because they assigned to RHS and connected to the gates which are in LHS
    for i in range(len(ConnectedGatesToLHS)):
        k=1
        while ConnectedGatesToLHS[i][k]!=0 and k<columns:#k<columns-->because"ConnectedGatesToLHS" array consists of columns cols. 
            if count_gate[ConnectedGatesToLHS[i][k]-1]==False:
                row_fake_pad_matrix+=1
                count_gate[ConnectedGatesToLHS[i][k]-1]=True
            k+=1            
        #count the pad names in "pad_matrix" array which connected to the gates in LHS
        k=0
        while pad_names_that_connect_to_gateID[AssignedGatesToLHS[i]][k]!=0:
            #"w" var. represents name of the pad that will be propagated
            w=pad_names_that_connect_to_gateID[AssignedGatesToLHS[i]][k]-1
            if count_pad[w]==False:
                row_fake_pad_matrix+=1
                count_pad[w]=True
            k+=1
    #count the gate names in "AssignedGatesToRHS" array which will be propagated, because they are in LHS and assigned to RHS
    for i in range(len(AssignedGatesToRHS)):       
        ga_no=AssignedGatesToRHS[i]
        if x_matrix[ga_no]<=50 and count_gate[ga_no]==False:
            row_fake_pad_matrix+=1
            count_gate[ga_no]=True       
    print("row_fake_pad_matrix for a region in the LHS",row_fake_pad_matrix)
    #fake_pad_matrix contains info.in this order: [IDOfThePropagatedELement,IsGateOrPad(0forgate,elseforpad),xcoordinate,ycoordinate]
    fake_pad_matrix=[[0 for i in range(4)]for k in range(row_fake_pad_matrix)]            
    row_no=0#then full "fake_pad_matrix"...
    count_gate=[False for i in range(NumOfGates)]
    count_pad=[False for i in range(NumOfPads)]         
    #first, do the Propagation for these gates which in the RHS and connect to LHS        
    for i in range(len(ConnectedGatesToLHS)):                
        if ConnectedGatesToLHS[i][1] != 0:#check either there are propagation or not
            k=1#if there is, check how many times
            while ConnectedGatesToLHS[i][k] !=0:#because the gate name in 0th location is to gate in LHS already
                k+=1
            for h in range(1,k):        
                if count_gate[(ConnectedGatesToLHS[i][h]-1)] == False:
                    fake_pad_matrix[row_no][0]=ConnectedGatesToLHS[i][h]
                    fake_pad_matrix[row_no][1]=0 #means that it's a propagated gate not a real pad
                    fake_pad_matrix[row_no][2]=50.0
                    fake_pad_matrix[row_no][3]=y_matrix[ConnectedGatesToLHS[i][h]-1]
                    row_no+=1
                    count_gate[(ConnectedGatesToLHS[i][h]-1)]=True
    #second, do the Propagation for these gates which in the LHS and assigned to the RHS
    for i in range(len(AssignedGatesToRHS)):
        ga_no=AssignedGatesToRHS[i]
        #check either there are propagation or not(if the gate with name "AssignedGatesToRHS[i]" in LHS or not) 
        if x_matrix[ga_no]<=50 and count_gate[ga_no]==False:
            fake_pad_matrix[row_no][0]=ga_no+1
            fake_pad_matrix[row_no][1]=0 #means that it's a propagated gate not a real pad
            fake_pad_matrix[row_no][2]=50.0
            fake_pad_matrix[row_no][3]=y_matrix[ga_no]
            row_no+=1       
    #third, check for the pad name that will  be propagation
    for i in range(len(AssignedGatesToLHS)):
        gate_no=AssignedGatesToLHS[i]  
        if is_gateID_connects_to_pad[gate_no]:#check either the gate name in "gate_no" var. connect to pad or not
            k=0 #if it is, check how many pads
            while pad_names_that_connect_to_gateID[gate_no][k]!=0:
                k+=1
            for h in range(k):
                pad_no=pad_names_that_connect_to_gateID[gate_no][h]-1#get the pad name
                if  count_pad[pad_no]==False:
                    #copy all its information from the pad_matrix "original info."
                    fake_pad_matrix[row_no][0]=pad_no+1
                    fake_pad_matrix[row_no][1]=pad_matrix[pad_no][1]
                    fake_pad_matrix[row_no][3]=pad_matrix[pad_no][3]
                    if pad_matrix[pad_no][2]>50:#check either this pad in RHS or not                        
                        fake_pad_matrix[row_no][2]=50.0#propagate it
                    else:# if it in the LHS, put it original x coordinate
                        fake_pad_matrix[row_no][2]=pad_matrix[pad_no][2]    
                    row_no+=1
                    count_pad[pad_no]=True                    
    return fake_pad_matrix                    
#the function returns the new pad matrix,that contains all info about the propagated gates and pads and the normal existing pads
#this function like the previous function, but for the region in the right.
def cont_step_for_RHS(ConnectedGatesToRHS):              
    row_fake_pad_matrix=0                
    count_gate=[False for i in range(NumOfGates)]
    count_pad=[False for i in range(NumOfPads)]
    #count the gate names in "ConnectedGatesToRHS" array which will be propagated, because they assigned to LHS and connected to the gates which are in RHS
    for i in range(len(ConnectedGatesToRHS)):
        k=1
        while ConnectedGatesToRHS[i][k]!=0 and k<columns:#k<columns-->because"ConnectedGatesToRHS" array consists of columns cols. 
            if count_gate[ConnectedGatesToRHS[i][k]-1]==False:
                row_fake_pad_matrix+=1
                count_gate[ConnectedGatesToRHS[i][k]-1]=True
            k+=1            
        #count the pad names in "pad_matrix" array which connected to the gates in RHS
        k=0
        while pad_names_that_connect_to_gateID[AssignedGatesToRHS[i]][k]!=0:
            w=pad_names_that_connect_to_gateID[AssignedGatesToRHS[i]][k]-1
            if count_pad[w]==False:
                row_fake_pad_matrix+=1
                count_pad[w]=True
            k+=1
    #count the gate names in "AssignedGatesToLHS" array which will be propagated, because they are in RHS and assigned to LHS
    for i in range(len(AssignedGatesToLHS)):       
        ga_no=AssignedGatesToLHS[i]
        if x_matrix[ga_no]>=50 and count_gate[ga_no]==False:
            row_fake_pad_matrix+=1
            count_gate[ga_no]=True       
    print("row_fake_pad_matrix for a region in the RHS",row_fake_pad_matrix)
    #fake_pad_matrix contains info.in this order: [IDOfThePropagatedELement,IsGateOrPad(0forgate,elseforpad),xcoordinate,ycoordinate]
    fake_pad_matrix=[[0 for i in range(4)]for k in range(row_fake_pad_matrix)]            
    row_no=0
    count_gate=[False for i in range(NumOfGates)]
    count_pad=[False for i in range(NumOfPads)]         
    #first, do the Propagation for these gates which in the RHS and connect to RHS        
    for i in range(len(ConnectedGatesToRHS)):                
        if ConnectedGatesToRHS[i][1] != 0:
            k=1
            while ConnectedGatesToRHS[i][k] !=0:
                k+=1
            for h in range(1,k):        
                if count_gate[(ConnectedGatesToRHS[i][h]-1)] == False:
                    fake_pad_matrix[row_no][0]=ConnectedGatesToRHS[i][h]
                    fake_pad_matrix[row_no][1]=0 #means that it's a propagated gate not a real pad
                    fake_pad_matrix[row_no][2]=50.0
                    fake_pad_matrix[row_no][3]=y_matrix[ConnectedGatesToRHS[i][h]-1]
                    row_no+=1
                    count_gate[(ConnectedGatesToRHS[i][h]-1)]=True
    #second, do the Propagation for these gates which in the RHS and assigned to the LHS
    for i in range(len(AssignedGatesToLHS)):
        ga_no=AssignedGatesToLHS[i] 
        if x_matrix[ga_no]>=50 and count_gate[ga_no]==False:#check either there are propagation or not(if the gate with name "AssignedGatesToLHS[i]" in RHS or not)
            fake_pad_matrix[row_no][0]=ga_no+1
            fake_pad_matrix[row_no][1]=0 #means that it's a propagated gate not a real pad
            fake_pad_matrix[row_no][2]=50.0
            fake_pad_matrix[row_no][3]=y_matrix[ga_no]
            row_no+=1       
    #third, check for the pad name that will  be propagation
    for i in range(len(AssignedGatesToRHS)):
        IsPadMatrixChanged=False
        gate_no=AssignedGatesToRHS[i]     
        if is_gateID_connects_to_pad[gate_no]:        #check either the gate name in "gate_no" var. connect to pad or not 
            k=0
            while pad_names_that_connect_to_gateID[gate_no][k]!=0:
                k+=1
            for h in range(k):
                pad_no=pad_names_that_connect_to_gateID[gate_no][h]-1
                if  count_pad[pad_no]==False:
                    #copy all its information from the pad_matrix "original info."
                    fake_pad_matrix[row_no][0]=pad_no+1
                    fake_pad_matrix[row_no][1]=pad_matrix[pad_no][1]
                    fake_pad_matrix[row_no][3]=pad_matrix[pad_no][3]
                    if pad_matrix[pad_no][2]<50:#check either this pad in LHS or not
                        fake_pad_matrix[row_no][2]=50.0#propagate it
                    else:# if it in the RHS, put it original x coordinate
                        fake_pad_matrix[row_no][2]=pad_matrix[pad_no][2]    
                    row_no+=1
                    count_pad[pad_no]=True                    
    return fake_pad_matrix                    
#the main function:
InputFileName="new1.txt"
OuputFileName1="new11"
OuputFileName2="new12"
OuputFileName3="new13"
f=open(InputFileName,"r") #put the name of the input file here 
netlist_lines=f.readlines()
#obtain the number of gates as integer
LenOfTheNumOfGates=0
while netlist_lines[0][LenOfTheNumOfGates]!=' ':
    LenOfTheNumOfGates+=1
i=0
NumOfGates=0
for i in range(LenOfTheNumOfGates):
    NumOfGates+=int(netlist_lines[0][i])*(10 ** (LenOfTheNumOfGates-(i+1)))
print("Printing general information from the input file:")
print("NumOfGates =",NumOfGates)
#obtain no. of nets as integer
LenOfTheNumOfNets=0
BeginOfNumOfNets=LenOfTheNumOfGates+1
k=BeginOfNumOfNets
while netlist_lines[0][k]!=' ':
    LenOfTheNumOfNets+=1
    k+=1
    if netlist_lines[0][k]=='\n':
        break
NumOfNets=0
for i in range(LenOfTheNumOfNets):
    NumOfNets+=int(netlist_lines[0][BeginOfNumOfNets+i])*(10 ** (LenOfTheNumOfNets-(i+1)))
print("NumOfNets =",NumOfNets)
#create an array that contains the ID of the connecting gates in each net
j=0
if NumOfNets > 50:
    columns=100
else:
    columns=10
gate_matrix=[[0 for i in range(columns)] for j in range(NumOfGates)]
net_matrix=[[0 for i in range(columns)] for j in range(NumOfNets)]
#to full net_matrix, we need to 1-D array which has cols that represent the location of saving ID gate
NumOfIDgatesInIDnet=[0 for i in range(NumOfNets)]

for GateNo in range(1,NumOfGates+1):
    i=0
    LenOfNumNetsConnected=0
    NumNetsConnected=0
    while netlist_lines[GateNo][i]!=' ':#skip the gate ID
        i+=1
    i+=1
    #obtain NumNetsConnected as integer type
    while netlist_lines[GateNo][i]!=' ':#determine the len. of the NumNetsConnected
        i+=1
        LenOfNumNetsConnected+=1
    i-=LenOfNumNetsConnected
    if  LenOfNumNetsConnected==1:
        NumNetsConnected=int(netlist_lines[GateNo][i])
        i+=2#to skip the space
    else:
        k=0
        for k in range(LenOfNumNetsConnected):
            NumNetsConnected+=int(netlist_lines[GateNo][i])*(10 ** (LenOfNumNetsConnected-(k+1)))
            i+=1     
    for k in range(NumNetsConnected): 
        #obtain the net ID as an integer type
        LenOfNetID=0
        Net_ID=0
        while netlist_lines[GateNo][i]!=' ':#determine the len. of the net ID
            i+=1
            LenOfNetID+=1
            if netlist_lines[GateNo][i]=='\n':
                break
        i-=LenOfNetID
        if LenOfNetID==1:
            Net_ID=int(netlist_lines[GateNo][i])
            i+=2#to skip space
        else:  
            for j in range(LenOfNetID):
                Net_ID+=int(netlist_lines[GateNo][i]) * (10**(LenOfNetID-(j+1)))
                i+=1
            i+=1#to skip space
        gate_matrix[GateNo-1][k]=Net_ID #full gate_matrix with the info. in the input file
        net_matrix[Net_ID-1][NumOfIDgatesInIDnet[Net_ID-1]]=GateNo#full net_matrix
        NumOfIDgatesInIDnet[Net_ID-1]+=1
#print this information if the given netlist small only
if columns==10:
    print("gate_matrix:")
    for row in gate_matrix:
        print(row)
    print("net_matrix:")
    for row in net_matrix:
        print(row)    
    print("NumOfIDgatesInIDnet:")
    for row in NumOfIDgatesInIDnet:
        print(row)
#obtain the number of Pads as an integer type
i=0
LenOfNumOfPads=0
while netlist_lines[NumOfGates+1][i]!=' ':
    LenOfNumOfPads+=1
    i+=1
    if netlist_lines[NumOfGates+1][i]=='\n':
        break
i-=LenOfNumOfPads
NumOfPads=0
for i in range(LenOfNumOfPads):
    NumOfPads+=int(netlist_lines[NumOfGates+1][i]) * (10**(LenOfNumOfPads-(i+1)))
print("NumOfPads=",NumOfPads)
#create an array that contains the all information of each Pad in this order: [ID Of Pad,connected to Net no.,X Coordinate,Y Coordinate]
pad_matrix=[[0 for i in range(4)] for j in range (NumOfPads)]
Pad_NO=0
for i in range(NumOfGates+2,NumOfGates+2+NumOfPads):
    k=0
    for h in range(4):#because there are 4 numbers in each line
        LenOfNum=0
        while netlist_lines[i][k]!=' ':#determine the length of the num
            LenOfNum+=1
            k+=1
            if netlist_lines[i][k]=='\n':
                break
        k-=LenOfNum
        for j in range(LenOfNum):#convert the string into integer type and save it in its location in the pad_matrix 
            pad_matrix[Pad_NO][h]+=int(netlist_lines[i][k]) * (10**(LenOfNum-(j+1)))    
            k+=1
        if netlist_lines[i][k]=='\n' :#check either you in the end of the string line or not
            break
        else:
            k+=1 #to skip the space
    Pad_NO+=1        
#remove later
if NumOfPads<30:
    print("pad_matrix:")
    for row in pad_matrix:
        print(row)
#create an array that tells either the gate connected to pad or not
#and if it is, tells how many they are and what their names
is_gateID_connects_to_pad=[False for i in range(NumOfGates)]
pad_names_that_connect_to_gateID=[[0 for i in range(columns)] for k in range(NumOfGates)]
NumOfIDpadsThatConnectToIDgate=[0 for i in range(NumOfGates)]
IDgate=0
for i in range(NumOfPads):#i represents name of pad
    #all the IDgates in the "NetNameThatWilBeChecked" var. connect to the pad number "i"
    NetNameThatWilBeChecked=pad_matrix[i][1]-1 
    #handle the IDgates one by one:
    for k in range(NumOfIDgatesInIDnet[NetNameThatWilBeChecked]):
        is_gateID_connects_to_pad[IDgate]=True
        IDgate=net_matrix[NetNameThatWilBeChecked][k]-1
        #save the IDgate in its corrsponding row in the "pad_names_that_connect_to_gateID" matrix    
        pad_names_that_connect_to_gateID[IDgate][NumOfIDpadsThatConnectToIDgate[IDgate]]=pad_matrix[i][0]
        NumOfIDpadsThatConnectToIDgate[IDgate]+=1
#remove later
if NumOfPads<30:
    print("pad_names_that_connect_to_gateID:")
    for row in pad_names_that_connect_to_gateID:
        print(row)
Weight1=WeightFunction(net_matrix,pad_matrix)#compute the weight of each net
print("Weight1:")
for row in Weight1:
    print(row)
print("===============")
A,C,bx,by,Order=A_C_bx_by_Matrices(NumOfGates,gate_matrix,net_matrix,NumOfIDgatesInIDnet,pad_matrix,Weight1)
#remove later
if columns==10:
    print("First C:")
    for row in C:
        print(row)    
    print("First A:")
    for row in A:
        print(row)
    print("First bx:")
    for row in bx:
        print(row)    
    print("First by:")
    for row in by:
        print(row)    
#solve for x and y vectors and print them
x_matrix = spsolve(coo_matrix(A).tocsr(), bx)# convert A into a sparse matrix in coordinate format,then compressed sparse row(csr),just to save time! 
y_matrix = spsolve(coo_matrix(A).tocsr(), by)
#remove later
print("x and y vectors, at the first time, have been saved in file with name:",OuputFileName1)
OP1=["0"for i in range(NumOfGates)]
for row in range(NumOfGates):
    OP1[row]="%d %.8f %.8f"%(row+1,x_matrix[row],y_matrix[row])
f1=open(OuputFileName1,"w")
for ele in OP1:
    f1.write(ele+'\n')
AssignedGatesToLHS,AssignedGatesToRHS=sortx(x_matrix,y_matrix)
#remove later
#print this information if the given netlist small only
if columns==10:
    print("=======================")
    print("Assignment Step:-")
    print("AssignedGatesToLHS:")
    print(AssignedGatesToLHS)    
    print("AssignedGatesToRHS:")
    print(AssignedGatesToRHS)
    print("=======================")
#obtain all info. about ConnectedGates in different regions 
#ConnectedGatesToLHS: contains the gate names, which are in RHS and connect to the gates in LHS,in this order: IDOfGateInLHS,IDOfGatesInRHS...
#ConnectedGatesToRHS: is the opposite of the first matrix
ConnectedGatesToLHS,ConnectedGatesToRHS=GatesConnectedInDifferentRegions( AssignedGatesToLHS, AssignedGatesToRHS)    
#containment step for the region in left
New_pad_matrix=cont_step_for_LHS(ConnectedGatesToLHS)
#remove later
print("New_pad_matrix For LHS region:")
for i in New_pad_matrix:
    print(i)
#create the new gate matrix      
NewNumOfGates=len(AssignedGatesToLHS)
New_gate_matrix=[[0 for i in range(columns)] for k in range(NumOfGates)]
for i in range(NewNumOfGates):
    for k in range(columns):
        New_gate_matrix[AssignedGatesToLHS[i]][k]=gate_matrix[AssignedGatesToLHS[i]][k]
#create the new net matrix by copying the original one and removing ID of the gates in RHS and the IDs of the propagated gates  
New_net_matrix=[[net_matrix[k][i]for i in range(columns)] for k in range(NumOfNets)] 
#removing ID of the gates in RHS first
for i in range(len(AssignedGatesToRHS)):
    g_no=AssignedGatesToRHS[i]+1
    for k in range(NumOfNets):
        for h in range(columns):
            if g_no == net_matrix[k][h]:
                New_net_matrix[k][h]=0
# second, removing the IDs of the propagated gates      
for i in range(len(New_pad_matrix)):    
    if New_pad_matrix[i][1]==0:
        g_no=New_pad_matrix[i][1]-1
        for k in range(NumOfNets):
            for h in range(columns):
                if g_no == net_matrix[k][h]:
                    New_net_matrix[k][h]=0
#reorder New_net_matrix to ensure that there is no zeroes between the the gate names in each net
for i in range(NumOfNets):
    ROW=[New_net_matrix[i][k] for k in range(columns)]
    SortedROW=sorted(ROW,reverse=True)
    for k in range(columns):
        New_net_matrix[i][k]=SortedROW[k]
#remove later
#print this information if the given netlist small only
if columns==10:
    print("New_net_matrix(LHS):")
    for i in New_net_matrix:
        print(i)
#create new NumOfIDgatesInIDnet    
New_NumOfIDgatesInIDnet=[0 for i in range(NumOfNets)]
for i in range(NumOfNets):
    for k in range(columns):    
        if New_net_matrix[i][k]!=0:
            New_NumOfIDgatesInIDnet[i]+=1
Weight2=WeightFunction(New_net_matrix,New_pad_matrix)#compute the weight of each net
#print this information if the given netlist small only
if columns==10:
    print("Weight2:")
    for row in Weight2:
        print(row)                                  
New_A,New_C,New_bx,New_by,Order=A_C_bx_by_Matrices(NewNumOfGates,New_gate_matrix,New_net_matrix,New_NumOfIDgatesInIDnet,New_pad_matrix,Weight2)
#solve for x and y vectors and print them
x_matrix_for_LHS = spsolve(coo_matrix(New_A).tocsr(), New_bx)
y_matrix_for_LHS = spsolve(coo_matrix(New_A).tocsr(), New_by)
#remove later
for i in range(NewNumOfGates):
    x_matrix[Order[i]-1]=x_matrix_for_LHS[i]
    y_matrix[Order[i]-1]=y_matrix_for_LHS[i]
#remove later
print("x and y vectors, at the second time, have been saved in file with name:",OuputFileName2)
OP2=["0"for i in range(NumOfGates)]
for row in range(NumOfGates):
    OP2[row]="%d %.8f %.8f"%(row+1,x_matrix[row],y_matrix[row])
f2=open(OuputFileName2,"w")
for ele in OP2:
    f2.write(ele+'\n')
print("====================")
#containment step for the region in right
New_pad_matrix=cont_step_for_RHS(ConnectedGatesToRHS)
#remove later
print("New_pad_matrix For RHS region:")
for i in New_pad_matrix:
    print(i)
#create the new gate matrix      
NewNumOfGates=len(AssignedGatesToRHS)
New_gate_matrix=[[0 for i in range(columns)] for k in range(NumOfGates)]
for i in range(NewNumOfGates):
    for k in range(columns):
        New_gate_matrix[AssignedGatesToRHS[i]][k]=gate_matrix[AssignedGatesToRHS[i]][k]
#by copying them and removing ID of the gates in the LHS, the IDs of the propagated gates(either they were in RHS or LHS)
New_net_matrix=[[net_matrix[k][i]for i in range(columns)] for k in range(NumOfNets)] 
#removing ID of the gates in LHS first
for i in range(len(AssignedGatesToLHS)):
    g_no=AssignedGatesToLHS[i]+1
    for k in range(NumOfNets):
        for h in range(columns):
            if g_no == net_matrix[k][h]:
                New_net_matrix[k][h]=0
# second, removing ID of the propagated gates      
for i in range(len(New_pad_matrix)):    
    if New_pad_matrix[i][1]==0:
        g_no=New_pad_matrix[i][1]-1
        for k in range(NumOfNets):
            for h in range(columns):
                if g_no == net_matrix[k][h]:
                    New_net_matrix[k][h]=0
#reorder New_net_matrix to ensure that there are no zeroes between the the gate names in each net
for i in range(NumOfNets):
    ROW=[New_net_matrix[i][k] for k in range(columns)]
    SortedROW=sorted(ROW,reverse=True)
    for k in range(columns):
        New_net_matrix[i][k]=SortedROW[k]
#remove later
#print this information if the given netlist small only
if columns==10:
    print("New_net_matrix(RHS):")
    for i in New_net_matrix:
        print(i)
#create new NumOfIDgatesInIDnet    
New_NumOfIDgatesInIDnet=[0 for i in range(NumOfNets)]
for i in range(NumOfNets):
    for k in range(columns):    
        if New_net_matrix[i][k]!=0:
            New_NumOfIDgatesInIDnet[i]+=1
Weight3=WeightFunction(New_net_matrix,New_pad_matrix)#compute the weight of each net
#print this information if the given netlist small only
if columns==10:
    print("Weight3:")
    for row in Weight3:
        print(row) 
New_A,New_C,New_bx,New_by,Order=A_C_bx_by_Matrices(NewNumOfGates,New_gate_matrix,New_net_matrix,New_NumOfIDgatesInIDnet,New_pad_matrix,Weight3)
#solve for x and y vectors and print them
x_matrix_for_RHS = spsolve(coo_matrix(New_A).tocsr(), New_bx)
y_matrix_for_RHS = spsolve(coo_matrix(New_A).tocsr(), New_by)
for i in range(NewNumOfGates):
    x_matrix[Order[i]-1]=x_matrix_for_RHS[i]
    y_matrix[Order[i]-1]=y_matrix_for_RHS[i]
#remove later
print("x and y vectors at the third QP(RHS):")
OP3=["0"for i in range(NumOfGates)]
for row in range(NumOfGates):
    OP3[row]="%d %.8f %.8f"%(row+1,x_matrix[row],y_matrix[row])
for row in OP3:
    print(row)
f3=open(OuputFileName3,"w")
for ele in OP3:
    f3.write(ele+'\n')
f.close()
f1.close()
f2.close()
f3.close()
print("x and y vectors, at the third time, have been saved in file with name:",OuputFileName3)